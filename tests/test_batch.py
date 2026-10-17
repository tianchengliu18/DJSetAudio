import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import extract_audio as app


class BatchTests(unittest.TestCase):
    def test_utf8_bom_comments_duplicates_and_url_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / '清单.txt'
            url = 'https://example.com/a?one=1&two=2#part'
            file.write_text('# 注释\n\n' + url + '\n' + url + '\n', encoding='utf-8-sig')
            args = app.parser().parse_args(['--batch', str(file)])
            urls, errors, duplicate = app.read_urls(args)
            self.assertEqual((urls, errors, duplicate), ([url], [], 1))

    def test_invalid_lines_block_all_downloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'urls.txt'
            file.write_text('https://example.com/ok\n"https://example.com/no"\nfile:///tmp/a\nhttps://user:secret@example.com/x\n', encoding='utf-8')
            with patch.object(app, 'execute') as execute, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                code = app.main(['--batch', str(file), '--output', str(Path(tmp) / 'audio')])
            self.assertEqual(code, 2)
            execute.assert_not_called()
            self.assertFalse((Path(tmp) / 'audio').exists())

    def test_dry_run_no_dependencies_no_network_no_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'audio'
            with patch.object(app, 'downloader', return_value=[]), patch.object(app, 'execute') as execute, contextlib.redirect_stdout(io.StringIO()):
                code = app.main(['--dry-run', '--output', str(dest), 'https://example.com/a'])
            self.assertEqual(code, 0)
            self.assertFalse(dest.exists())
            execute.assert_not_called()

    def test_failure_continues_and_produces_retry_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'audio'
            output_file = Path(tmp) / 'result.mp3'
            output_file.write_bytes(b'test-only')
            with patch.object(app, 'downloader', return_value=['yt-dlp']), patch.object(app, 'media_tool', return_value='tool'), patch.object(app, 'execute', side_effect=[(1, []), (0, [str(output_file)]), (0, [])]), contextlib.redirect_stdout(io.StringIO()):
                code = app.main(['--jobs', '1', '--output', str(dest), 'https://example.com/fail', 'https://example.com/ok', 'https://example.com/skipped'])
            self.assertEqual(code, 1)
            run = next((dest / '.dj-work/runs').iterdir())
            report = json.loads((run / 'results.json').read_text())
            self.assertEqual([r['status'] for r in report['results']], ['failed', 'completed', 'skipped_or_no_output'])
            self.assertEqual((run / 'failed.txt').read_text(), 'https://example.com/fail\n')
            self.assertFalse((dest / '.dj-work/run.lock').exists())

    def test_interrupt_releases_lock_and_keeps_partial_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            with patch.object(app, 'downloader', return_value=['yt-dlp']), patch.object(app, 'media_tool', return_value='tool'), patch.object(app, 'execute', side_effect=KeyboardInterrupt), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(KeyboardInterrupt):
                    app.main(['--jobs', '1', '--output', str(dest), 'https://example.com/a'])
            self.assertFalse((dest / '.dj-work/run.lock').exists())
            report = json.loads(next((dest / '.dj-work/runs').glob('*/results.json')).read_text())
            self.assertEqual(report['processed_count'], 0)

    def test_existing_lock_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / '.dj-work'
            state.mkdir()
            (state / 'run.lock').write_text('another-process')
            with patch.object(app, 'downloader', return_value=['yt-dlp']), patch.object(app, 'media_tool', return_value='tool'), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'locked by another task'):
                    app.main(['--output', tmp, 'https://example.com/a'])
            self.assertEqual((state / 'run.lock').read_text(), 'another-process')

    def test_simulation_no_archive_and_format_history_is_separate(self):
        args = app.parser().parse_args(['--simulate'])
        cmd = app.build_command(args, 'https://example.com/a', ['yt-dlp'])
        self.assertNotIn('--download-archive', cmd)
        self.assertIn('--simulate', cmd)
        mp3 = app.build_command(app.parser().parse_args(['--format', 'mp3']), 'https://example.com/a', ['yt-dlp'])
        best = app.build_command(app.parser().parse_args([]), 'https://example.com/a', ['yt-dlp'])
        self.assertNotEqual(mp3[mp3.index('--download-archive') + 1], best[best.index('--download-archive') + 1])
        self.assertEqual(mp3[-2:], ['--', 'https://example.com/a'])

    def test_default_jobs_run_multiple_urls_concurrently_and_keep_input_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'audio'
            guard = threading.Lock()
            release = threading.Event()
            active = 0
            max_active = 0

            def fake_execute(command, logfile, prefix=''):
                nonlocal active, max_active
                with guard:
                    active += 1
                    max_active = max(max_active, active)
                    if active >= 2:
                        release.set()
                release.wait(timeout=1)
                time.sleep(0.01)
                with guard:
                    active -= 1
                return 0, []

            urls = ['https://example.com/a', 'https://example.com/b', 'https://example.com/c']
            with patch.object(app, 'downloader', return_value=['yt-dlp']), patch.object(app, 'media_tool', return_value='tool'), patch.object(app, 'execute', side_effect=fake_execute), contextlib.redirect_stdout(io.StringIO()):
                code = app.main(['--output', str(dest), *urls])
            self.assertEqual(code, 0)
            self.assertGreaterEqual(max_active, 2)
            report = json.loads(next((dest / '.dj-work/runs').glob('*/results.json')).read_text())
            self.assertEqual(report['jobs'], 3)
            self.assertEqual([item['url'] for item in report['results']], urls)

    def test_interactive_progress_repaints_in_place(self):
        output = io.StringIO()
        display = app.ProgressDisplay(2, 5, stream=output, enabled=True)
        display.start(1, 'Extracting')
        display.start(2, 'Extracting')
        display.handle(1, '[download] 2.9% at 105.73KiB/s ETA 06:37')
        display.handle(2, '[download] 13.3% at 115.08KiB/s ETA 08:18')
        display.finish(1, 'completed')
        display.close()
        rendered = output.getvalue()
        self.assertIn('\033[2A', rendered)
        self.assertIn('[1/5] [download] 2.9%', rendered)
        self.assertIn('[2/5] [download] 13.3%', rendered)
        self.assertEqual(rendered.count('[1/5] Result: completed'), 1)

    def test_chinese_language_help_and_runtime_output(self):
        self.assertIn('位置参数：', app.parser('zh').format_help())
        terminal = io.StringIO()
        with patch.object(app, 'downloader', return_value=[]), contextlib.redirect_stdout(terminal):
            code = app.main(['--language', 'zh', '--dry-run', 'https://example.com/a'])
        self.assertEqual(code, 0)
        self.assertIn('有效链接：1', terminal.getvalue())
        progress = io.StringIO()
        display = app.ProgressDisplay(1, 1, 'zh', stream=progress, enabled=True)
        display.start(1, '提取中')
        display.finish(1, 'completed')
        display.close()
        self.assertIn('[1/1] 结果：已完成', progress.getvalue())


if __name__ == '__main__':
    unittest.main()
