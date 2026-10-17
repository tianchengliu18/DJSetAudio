#!/usr/bin/env python3
"""Extract audio from a TXT URL list by invoking yt-dlp as a subprocess."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from urllib.parse import urlsplit
import uuid

ROOT = Path(__file__).resolve().parent
MARKER = "DJWORK_FILE:"
LANGUAGE_FILE = ROOT / "language.txt"

MESSAGES = {
    "en": {
        "job_count": "concurrency must be an integer from 1 to 16",
        "result": "Result: {status}",
        "description": "Extract audio from URLs listed one per line in a TXT file. Defaults to urls.txt in this project.",
        "urls_help": "optional HTTP(S) URLs supplied directly",
        "batch_help": "UTF-8 TXT file with one URL per line; may be combined with direct URLs",
        "output_help": "output directory; defaults to audio in this project",
        "format_help": "output format; best preserves the source codec when possible",
        "jobs_help": "number of URLs processed concurrently, 1-16; default: 3",
        "language_help": "interface language; defaults to language.txt",
        "dry_run_help": "validate input and print commands without network access or file writes",
        "simulate_help": "read online metadata without downloading media or updating history",
        "doctor_help": "check local dependencies and versions without reading URLs or using the network",
        "ffmpeg_help": "directory containing both ffmpeg and ffprobe",
        "js_help": "JavaScript runtime; auto prefers Deno, then Node; Node 22+ required",
        "verbose_help": "show yt-dlp diagnostics; inspect logs for private data before sharing",
        "archive_help": "ignore completion history to restore deleted audio; existing files are not overwritten",
        "command_line": "command line",
        "encoding": "The TXT file must be UTF-8. Save it as UTF-8 plain text and try again.",
        "invalid_url": "{where}: expected a complete HTTP(S) URL without quotes, spaces, or embedded credentials.",
        "youtube_note": "Note: Full YouTube support also requires a JavaScript runtime and matching EJS package. See README.md.",
        "ejs_missing": "yt-dlp-ejs: Not found. Run the setup script to update the default dependency group.",
        "external_ejs": "EJS: An external yt-dlp is in use; verify EJS support for that installation method.",
        "doctor_scope": "This check only verifies local dependencies; it does not prove that a particular platform URL is supported.",
        "exclusive": "--dry-run and --simulate cannot be used together",
        "valid_urls": "Valid URLs: {count}; duplicates removed: {duplicates}.",
        "fix_invalid": "Fix the invalid entries above. No extraction was started.",
        "no_urls": "Add one URL per line to urls.txt, then run the command again.",
        "missing_ytdlp": "yt-dlp was not found. Run the setup script for your operating system first.",
        "missing_media": "{name} was not found. Install it as described in README.md or use --ffmpeg-location.",
        "locked": "The output directory is locked by another task: {lock}. Confirm that no task is running before removing a stale lock.",
        "checking": "Checking",
        "extracting": "Extracting",
        "summary": "Summary:",
        "report": "Report and failed-URL retry list: {path}",
        "skip_hint": "skipped_or_no_output usually means the item is already in completion history; check its log to confirm.",
        "interrupted": "Interrupted. Run the command again to continue unfinished items.",
        "error": "Error: {error}",
        "status_completed": "completed",
        "status_parsed": "parsed",
        "status_skipped_or_no_output": "skipped_or_no_output",
        "status_failed": "failed",
    },
    "zh": {
        "job_count": "并发数必须是 1 到 16 的整数",
        "result": "结果：{status}",
        "description": "从 TXT 中按每行一个 URL 批量提取音轨。默认读取项目内的 urls.txt。",
        "urls_help": "可选：直接提供一个或多个 HTTP(S) URL",
        "batch_help": "UTF-8 TXT，每行一个 URL；可与直接 URL 合并",
        "output_help": "保存目录；默认使用项目内的 audio",
        "format_help": "输出格式；best 会尽量保留来源音频编码",
        "jobs_help": "同时处理的链接数，1-16；默认 3",
        "language_help": "界面语言；默认读取 language.txt",
        "dry_run_help": "只校验输入并显示命令；不联网、不写文件",
        "simulate_help": "联网读取元数据；不下载媒体、不更新完成历史",
        "doctor_help": "检查本地依赖和版本；不读取链接、不联网",
        "ffmpeg_help": "同时包含 ffmpeg 和 ffprobe 的目录",
        "js_help": "JavaScript 运行环境；auto 优先 Deno，其次 Node；Node 需 22+",
        "verbose_help": "显示 yt-dlp 诊断；分享日志前请检查私人信息",
        "archive_help": "忽略完成历史以恢复误删音频；仍不覆盖已有文件",
        "command_line": "命令行",
        "encoding": "TXT 文件必须使用 UTF-8 编码。请另存为 UTF-8 纯文本后重试。",
        "invalid_url": "{where}：需要完整的 HTTP(S) URL，且不能带引号、空格或账号密码。",
        "youtube_note": "提示：完整支持 YouTube 还需要 JavaScript 运行环境和匹配的 EJS 包，详见 README.md。",
        "ejs_missing": "yt-dlp-ejs：未找到。请运行安装脚本更新默认依赖组。",
        "external_ejs": "EJS：当前使用外部 yt-dlp；请按其安装方式核实 EJS 支持。",
        "doctor_scope": "此检查只验证本地依赖，不能证明某个平台链接一定可以解析。",
        "exclusive": "--dry-run 和 --simulate 不能同时使用",
        "valid_urls": "有效链接：{count}；已移除重复链接：{duplicates}。",
        "fix_invalid": "请先修正以上无效条目；本次未开始提取。",
        "no_urls": "请在 urls.txt 中每行填写一个 URL，然后重新运行。",
        "missing_ytdlp": "未找到 yt-dlp。请先运行当前操作系统对应的安装脚本。",
        "missing_media": "未找到 {name}。请按 README.md 安装，或使用 --ffmpeg-location 指定位置。",
        "locked": "输出目录已被另一个任务锁定：{lock}。请确认没有任务运行，再删除遗留锁文件。",
        "checking": "检查中",
        "extracting": "提取中",
        "summary": "汇总：",
        "report": "报告和失败链接重试清单：{path}",
        "skip_hint": "skipped_or_no_output 通常表示该项目已存在于完成历史中；请查看对应日志确认。",
        "interrupted": "任务已中断。再次运行可继续未完成项目。",
        "error": "错误：{error}",
        "status_completed": "已完成",
        "status_parsed": "已解析",
        "status_skipped_or_no_output": "已跳过或无输出",
        "status_failed": "失败",
    },
}


def message(language: str, key: str, **values) -> str:
    return MESSAGES[language][key].format(**values)


def selected_language(argv: list[str] | None = None) -> str:
    configured = os.environ.get("DJSETAUDIO_LANGUAGE", "").strip().lower()
    if not configured and LANGUAGE_FILE.is_file():
        configured = LANGUAGE_FILE.read_text(encoding="utf-8").strip().lower()
    language = configured if configured in MESSAGES else "en"
    arguments = sys.argv[1:] if argv is None else argv
    for index, argument in enumerate(arguments):
        if argument == "--language" and index + 1 < len(arguments):
            language = arguments[index + 1]
        elif argument.startswith("--language="):
            language = argument.split("=", 1)[1]
    return language if language in MESSAGES else "en"


class LocalizedArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, language: str = "en", **kwargs):
        self.language = language
        super().__init__(*args, **kwargs)

    def format_help(self) -> str:
        output = super().format_help()
        if self.language == "zh":
            output = output.replace("usage:", "用法：", 1)
            output = output.replace("positional arguments:", "位置参数：")
            output = output.replace("options:", "选项：")
            output = output.replace("show this help message and exit", "显示帮助并退出")
        return output

    def format_usage(self) -> str:
        output = super().format_usage()
        return output.replace("usage:", "用法：", 1) if self.language == "zh" else output

    def error(self, error_message: str) -> None:
        if self.language != "zh":
            super().error(error_message)
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: 错误：{error_message}\n")


def job_count(value: str, language: str = "en") -> int:
    try:
        count = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(message(language, "job_count")) from exc
    if not 1 <= count <= 16:
        raise argparse.ArgumentTypeError(message(language, "job_count"))
    return count


class ProgressDisplay:
    """Refresh concurrent tasks in place while execute preserves full logs."""

    def __init__(self, rows: int, total: int, language: str = "en", stream=None, enabled: bool | None = None):
        self.rows = max(1, rows)
        self.total = total
        self.language = language
        self.stream = stream or sys.stdout
        self.enabled = self.stream.isatty() if enabled is None else enabled
        self.lines: dict[int, str] = {}
        self.drawn = False
        self.lock = threading.RLock()

    def _write(self, value: str) -> None:
        self.stream.write(value)
        self.stream.flush()

    def _erase(self) -> None:
        if not self.drawn:
            return
        self._write(f"\033[{self.rows}A" + "\r\033[2K\n" * self.rows)
        self.drawn = False

    def _draw(self) -> None:
        if not self.enabled or not self.lines:
            return
        if self.drawn:
            self._write(f"\033[{self.rows}A")
        width = max(20, shutil.get_terminal_size((120, 20)).columns - 1)
        visible = [self.lines[index][:width] for index in sorted(self.lines)[:self.rows]]
        visible.extend([""] * (self.rows - len(visible)))
        self._write("".join(f"\r\033[2K{line}\n" for line in visible))
        self.drawn = True

    def start(self, index: int, action: str) -> None:
        label = f"[{index}/{self.total}]"
        with self.lock:
            if self.enabled:
                self.lines[index] = f"{label} {action}…"
                self._draw()
            else:
                self._write(f"{label} {action}…\n")

    def handle(self, index: int, line: str) -> None:
        if not line:
            return
        label = f"[{index}/{self.total}]"
        is_progress = line.startswith("[download]") and "%" in line
        with self.lock:
            if is_progress:
                if self.enabled:
                    self.lines[index] = f"{label} {line}"
                    self._draw()
                return
            if self.enabled:
                self._erase()
            self._write(f"{label} {line}\n")
            if self.enabled:
                self._draw()

    def finish(self, index: int, status: str) -> None:
        label = f"[{index}/{self.total}]"
        shown_status = message(self.language, f"status_{status}")
        with self.lock:
            if self.enabled:
                self._erase()
                self.lines.pop(index, None)
            self._write(f"{label} {message(self.language, 'result', status=shown_status)}\n")
            if self.enabled:
                self._draw()

    def close(self) -> None:
        with self.lock:
            if self.enabled:
                self._erase()
                self.lines.clear()


def parser(language: str | None = None) -> argparse.ArgumentParser:
    language = language or selected_language([])
    p = LocalizedArgumentParser(description=message(language, "description"), language=language)
    p.add_argument("urls", nargs="*", help=message(language, "urls_help"))
    p.add_argument("--batch", type=Path, help=message(language, "batch_help"))
    p.add_argument("--output", type=Path, default=ROOT / "audio", help=message(language, "output_help"))
    p.add_argument("--format", choices=["best", "mp3", "m4a", "flac"], default="best", help=message(language, "format_help"))
    p.add_argument("--jobs", type=lambda value: job_count(value, language), default=3, metavar="N", help=message(language, "jobs_help"))
    p.add_argument("--language", choices=["en", "zh"], default=language, help=message(language, "language_help"))
    p.add_argument("--dry-run", action="store_true", help=message(language, "dry_run_help"))
    p.add_argument("--simulate", action="store_true", help=message(language, "simulate_help"))
    p.add_argument("--doctor", action="store_true", help=message(language, "doctor_help"))
    p.add_argument("--ffmpeg-location", type=Path, help=message(language, "ffmpeg_help"))
    p.add_argument("--js-runtime", choices=["auto", "deno", "node"], default="auto", help=message(language, "js_help"))
    p.add_argument("--verbose", action="store_true", help=message(language, "verbose_help"))
    p.add_argument("--no-archive", action="store_true", help=message(language, "archive_help"))
    return p


def read_urls(args: argparse.Namespace) -> tuple[list[str], list[str], int]:
    entries = [(message(args.language, "command_line"), url) for url in args.urls]
    batch = args.batch or (ROOT / "urls.txt" if not args.urls else None)
    if batch:
        try:
            lines = batch.expanduser().read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError as exc:
            raise ValueError(message(args.language, "encoding")) from exc
        entries.extend((f"{batch.name}:{i}", line) for i, line in enumerate(lines, 1))
    urls, errors, seen, duplicates = [], [], set(), 0
    for where, raw in entries:
        url = raw.strip()
        if not url or url.startswith("#"):
            continue
        try:
            parsed = urlsplit(url)
            valid = parsed.scheme.lower() in ("http", "https") and bool(parsed.hostname)
            valid = valid and not any(c.isspace() or ord(c) < 32 for c in url)
            valid = valid and not parsed.username and not parsed.password
            _ = parsed.port  # Validate malformed ports.
        except ValueError:
            valid = False
        if not valid:
            errors.append(message(args.language, "invalid_url", where=where))
        elif url in seen:
            duplicates += 1
        else:
            seen.add(url)
            urls.append(url)
    return urls, errors, duplicates


def downloader() -> list[str]:
    if importlib.util.find_spec("yt_dlp"):
        return [sys.executable, "-m", "yt_dlp"]
    executable = shutil.which("yt-dlp")
    return [executable] if executable else []


def media_tool(name: str, location: Path | None) -> str | None:
    if location:
        path = location.expanduser().resolve() / (name + (".exe" if os.name == "nt" else ""))
        return str(path) if path.is_file() else None
    return shutil.which(name)


def version(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
        output = (result.stdout or result.stderr).splitlines()
        return output[0] if result.returncode == 0 and output else "Could not run"
    except (OSError, subprocess.TimeoutExpired):
        return "Could not run"


def js_runtime(args: argparse.Namespace) -> str:
    if args.js_runtime != "auto":
        return args.js_runtime
    return "deno" if shutil.which("deno") else ("node" if shutil.which("node") else "deno")


def doctor(args: argparse.Namespace) -> int:
    language = args.language
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    cmd = downloader()
    missing = not cmd
    ytdlp_version = version(cmd + ["--version"]) if cmd else "Not found"
    print("yt-dlp:", ytdlp_version)
    missing |= ytdlp_version == "Could not run"
    for name in ("ffmpeg", "ffprobe"):
        executable = media_tool(name, args.ffmpeg_location)
        value = version([executable, "-version"]) if executable else "Not found"
        print(f"{name}: {value}")
        missing |= value in ("Not found", "Could not run")
    selected_runtime = js_runtime(args)
    runtime = shutil.which(selected_runtime)
    runtime_version = version([runtime, "--version"]) if runtime else "Not found"
    print(f"{selected_runtime}: {runtime_version}")
    if not runtime:
        print(message(language, "youtube_note"))
    if importlib.util.find_spec("yt_dlp"):
        try:
            from importlib.metadata import version as package_version
            print("yt-dlp-ejs:", package_version("yt-dlp-ejs"))
        except Exception:
            print(message(language, "ejs_missing"))
    else:
        print(message(language, "external_ejs"))
    print(message(language, "doctor_scope"))
    return 2 if missing else 0


def build_command(args: argparse.Namespace, url: str, base: list[str]) -> list[str]:
    dest = args.output.expanduser().resolve()
    cmd = base + [
        "--ignore-config", "--no-playlist", "--playlist-items", "1",
        "--match-filters", "!is_live",
        "--no-overwrites", "--no-post-overwrites", "--continue",
        "--abort-on-unavailable-fragments", "--retries", "5", "--fragment-retries", "5",
        "--socket-timeout", "30", "--windows-filenames", "--trim-filenames", "180",
        "--no-cache-dir", "--newline", "--progress-delta", "0.2", "--js-runtimes", js_runtime(args),
        "-f", "bestaudio/best", "-x", "--audio-format", args.format,
        "-P", str(dest / args.format),
        "-o", "%(title).120B [%(extractor_key)s-%(id)s].%(ext)s",
    ]
    if args.format == "mp3":
        cmd += ["--audio-quality", "0"]
    if args.ffmpeg_location:
        cmd += ["--ffmpeg-location", str(args.ffmpeg_location.expanduser().resolve())]
    if args.verbose:
        cmd += ["--verbose"]
    if args.simulate:
        cmd += ["--simulate", "--print", "%(title)s | %(id)s | %(ext)s"]
    else:
        cmd += ["--no-simulate", "--progress", "--print", f"after_move:{MARKER}%(filepath)j"]
        if not args.no_archive:
            cmd += ["--download-archive", str(dest / ".dj-work" / f"archive-{args.format}.txt")]
    return cmd + ["--", url]


def execute(command: list[str], logfile: Path, line_handler=None) -> tuple[int, list[str]]:
    files = []
    environment = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
    with logfile.open("w", encoding="utf-8") as log:
        child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, encoding="utf-8", errors="replace", env=environment)
        try:
            assert child.stdout is not None
            for line in child.stdout:
                log.write(line)
                log.flush()
                if line.startswith(MARKER):
                    try:
                        files.append(json.loads(line[len(MARKER):]))
                    except json.JSONDecodeError:
                        pass
                else:
                    rendered = line.rstrip()
                    if line_handler:
                        line_handler(rendered)
                    else:
                        print(rendered, flush=True)
            return child.wait(), files
        finally:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            if child.stdout:
                child.stdout.close()


def main(argv: list[str] | None = None) -> int:
    language = selected_language(argv)
    cli = parser(language)
    args = cli.parse_args(argv)
    language = args.language
    if args.dry_run and args.simulate:
        cli.error(message(language, "exclusive"))
    if args.doctor:
        return doctor(args)
    urls, errors, duplicates = read_urls(args)
    print(message(language, "valid_urls", count=len(urls), duplicates=duplicates))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(message(language, "fix_invalid"), file=sys.stderr)
        return 2
    if not urls:
        print(message(language, "no_urls"), file=sys.stderr)
        return 2
    base = downloader()
    if args.dry_run:
        for url in urls:
            # A JSON array preserves argument boundaries and is not presented as a pasteable shell command.
            print(json.dumps(build_command(args, url, base or ["yt-dlp"]), ensure_ascii=False))
        return 0
    if not base:
        raise ValueError(message(language, "missing_ytdlp"))
    if not args.simulate:
        for name in ("ffmpeg", "ffprobe"):
            if not media_tool(name, args.ffmpeg_location):
                raise ValueError(message(language, "missing_media", name=name))
    dest = args.output.expanduser().resolve()
    state = dest / ".dj-work"
    state.mkdir(parents=True, exist_ok=True)
    lock = state / "run.lock"
    try:
        lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError(message(language, "locked", lock=lock)) from None
    with os.fdopen(lock_fd, "w") as handle:
        handle.write(str(os.getpid()))
    results: list[dict[str, object]] = []
    run_dir = state / "runs" / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
    display = ProgressDisplay(min(args.jobs, len(urls)), len(urls), language)
    try:
        run_dir.mkdir(parents=True)

        def process_one(index: int, url: str) -> tuple[int, dict[str, object]]:
            display.start(index, message(language, "checking") if args.simulate else message(language, "extracting"))
            log = run_dir / f"{index:04d}.log"
            code, files = execute(build_command(args, url, base), log,
                                  lambda line: display.handle(index, line))
            if code == 0 and args.simulate:
                status = "parsed"
            elif code == 0 and files and all(Path(path).is_file() for path in files):
                status = "completed"
            elif code == 0 and not files:
                status = "skipped_or_no_output"
            else:
                status = "failed"
            result = {"url": url, "status": status, "exit_code": code, "files": files, "log": log.name}
            display.finish(index, status)
            return index, result

        result_slots: list[dict[str, object] | None] = [None] * len(urls)

        def store_result(result_index: int, result: dict[str, object]) -> None:
            result_slots[result_index - 1] = result
            results[:] = [item for item in result_slots if item is not None]

        if args.jobs == 1:
            for index, url in enumerate(urls, 1):
                result_index, result = process_one(index, url)
                store_result(result_index, result)
        else:
            workers = min(args.jobs, len(urls))
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="dj-download") as pool:
                futures = [pool.submit(process_one, index, url) for index, url in enumerate(urls, 1)]
                try:
                    for future in as_completed(futures):
                        result_index, result = future.result()
                        store_result(result_index, result)
                except BaseException:
                    for future in futures:
                        future.cancel()
                    raise
    finally:
        try:
            display.close()
            if run_dir.exists():
                report = {"mode": "simulate" if args.simulate else "extract", "format": args.format, "jobs": args.jobs,
                          "input_count": len(urls), "processed_count": len(results), "results": results}
                (run_dir / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                failed = [r["url"] for r in results if r["status"] == "failed"]
                (run_dir / "failed.txt").write_text("".join(url + "\n" for url in failed), encoding="utf-8")
        finally:
            lock.unlink(missing_ok=True)
    counts = {status: sum(r["status"] == status for r in results)
              for status in ("completed", "parsed", "skipped_or_no_output", "failed")}
    shown_counts = {message(language, f"status_{status}"): count for status, count in counts.items()}
    print(f"\n{message(language, 'summary')}", json.dumps(shown_counts, ensure_ascii=False))
    print(message(language, "report", path=run_dir))
    print(message(language, "skip_hint"))
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    active_language = selected_language()
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n" + message(active_language, "interrupted"), file=sys.stderr)
        sys.exit(130)
    except (OSError, ValueError) as exc:
        print(message(active_language, "error", error=exc), file=sys.stderr)
        sys.exit(2)
