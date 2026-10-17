"""Real toolchain integration test using only media synthesized locally by FFmpeg."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def run(*args):
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
    return result


def reports(dest):
    return sorted((dest / '.dj-work/runs').glob('*/results.json'))


def main():
    with tempfile.TemporaryDirectory(prefix='DJSetAudio-本地测试-') as tmp:
        root = Path(tmp)
        source = root / 'source'
        source.mkdir()
        generated = run('ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=160x90:r=10', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2', '-t', '2', '-c:v', 'mpeg4', '-c:a', 'aac', '-shortest', str(source / 'synthetic.mp4'))
        assert generated.returncode == 0, generated.stderr
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(source)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f'http://127.0.0.1:{server.server_port}/synthetic.mp4'
            missing = f'http://127.0.0.1:{server.server_port}/missing.mp4'
            batch = root / '清单.txt'
            batch.write_text(f'# 合成素材\n{missing}\n{url}\n{url}\n', encoding='utf-8-sig')
            dest = root / '音轨 输出'
            base = [sys.executable, str(ROOT / 'extract_audio.py'), '--batch', str(batch), '--output', str(dest)]
            first = run(*base, '--format', 'mp3')
            assert first.returncode == 1, first.stdout + first.stderr
            report = json.loads(reports(dest)[0].read_text())
            assert [r['status'] for r in report['results']] == ['failed', 'completed'], report
            assert (reports(dest)[0].parent / 'failed.txt').read_text() == missing + '\n'
            mp3 = Path(report['results'][1]['files'][0])
            probe = run('ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(mp3))
            info = json.loads(probe.stdout)
            assert info['streams'][0]['codec_name'] == 'mp3', info
            assert not any(s['codec_type'] == 'video' for s in info['streams']), info
            assert 1.8 < float(info['format']['duration']) < 2.5, info
            mtime = mp3.stat().st_mtime_ns
            # Retry only the successful URL to verify archive skipping without rewriting the file.
            batch.write_text(url + '\n', encoding='utf-8')
            second = run(*base, '--format', 'mp3')
            assert second.returncode == 0, second.stdout + second.stderr
            assert mp3.stat().st_mtime_ns == mtime
            statuses = [json.loads(p.read_text())['results'][0]['status'] for p in reports(dest)]
            assert 'skipped_or_no_output' in statuses, statuses
            # A different format must use completion history independent of MP3.
            best = run(*base)
            assert best.returncode == 0, best.stdout + best.stderr
            assert list((dest / 'best').glob('*.m4a')), best.stdout
            # Simulation must not create completion history or media for the requested format.
            simulation = run(*base, '--simulate', '--format', 'flac')
            assert simulation.returncode == 0, simulation.stdout + simulation.stderr
            assert not (dest / '.dj-work/archive-flac.txt').exists()
            assert not (dest / 'flac').exists()
            print(json.dumps({'result': 'PASS', 'checks': ['UTF-8 BOM / Unicode and spaced paths', 'duplicate URL removal', 'continue after a 404', 'download real video and extract MP3', 'ffprobe verifies audio-only output of about 2 seconds', 'rerun skips without rewriting output', 'independent completion history by format', 'best extracts M4A', 'simulation writes no media or completion history'], 'media_source': 'synthesized locally by FFmpeg; no external recordings'}, ensure_ascii=False, indent=2))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == '__main__':
    main()
