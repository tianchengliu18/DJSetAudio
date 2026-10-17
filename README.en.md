# DJSetAudio

English | [简体中文](README.zh-CN.md)

**Batch-download and extract audio from a TXT list of media URLs.**

Put authorized video or audio URLs in `urls.txt`, run one command, and receive ready-to-use audio files in `audio/`.

`urls.txt` → concurrent downloads → FFmpeg audio extraction → MP3, M4A, FLAC, or source-quality audio

- Runs locally on macOS and Windows.
- Downloads three URLs concurrently by default with fixed-line live progress.
- Remembers completed items, resumes supported transfers, and writes retry reports for failures.

DJSetAudio runs locally with **yt-dlp + FFmpeg**. It extracts the complete audio track; it does not identify songs, split a DJ set into tracks, separate stems, bypass DRM, or bypass payment and access controls. Platform support can change over time.

## Install on macOS

Install Python, FFmpeg, and Deno with Homebrew:

```bash
brew install python ffmpeg deno
cd "/path/to/DJSetAudio"
bash scripts/setup-macos.sh
bash run.sh --doctor
```

After setup, edit `urls.txt` and run:

```bash
bash run.sh
```

You can also double-click `Start.command`. If macOS does not allow it to run, use `chmod +x Start.command` after reviewing the script.

## Install on Windows 10/11

Install Python 3.10 or newer, then install FFmpeg and Deno in PowerShell:

```powershell
winget install --exact --id Gyan.FFmpeg --source winget
winget install --exact --id DenoLand.Deno --source winget
cd "C:\path\to\DJSetAudio"
.\scripts\setup-windows.ps1
.\run.ps1 --doctor
```

After setup, edit `urls.txt` and run `.\run.ps1`, or double-click `Start.cmd`.

## URL list

Use UTF-8 plain text with one complete HTTP(S) URL per line:

```text
# Comments and blank lines are ignored
https://example.com/my-authorized-set-1.mp4
https://example.com/my-authorized-set-2.mp3
```

Duplicate URLs are removed. Invalid entries stop the run before any download begins. URLs, logs, and reports may contain private tokens, so inspect them before sharing.

## Preview and download

```bash
bash run.sh --dry-run
bash run.sh --simulate
bash run.sh
```

`--dry-run` validates input without network access or file writes. `--simulate` reads online metadata without downloading media or updating completion history.

Common options:

| Task | Option |
| --- | --- |
| Export MP3 | `--format mp3` |
| Export M4A | `--format m4a` |
| Export FLAC | `--format flac` |
| Change output directory | `--output "/path/to/music"` |
| Change concurrent tasks | `--jobs 5` (1–16; default 3) |
| Use another TXT list | `--batch "/path/to/list.txt"` |
| Ignore completion history | `--no-archive` |
| Show diagnostics | `--verbose` |
| Switch interface language | `--language zh` or `--language en` |

The `best` format preserves the source audio codec when possible. MP3 uses high-quality variable bitrate. FLAC cannot restore quality already lost in a compressed source.

## Progress, retries, and reports

In an interactive terminal, each active download uses one fixed line. Percentage, speed, and ETA refresh in place. Full raw output is retained in a separate log for each URL.

Downloads go to `audio/best`, `audio/mp3`, `audio/m4a`, or `audio/flac`. Run metadata is stored under `audio/.dj-work/runs`. Each run contains `results.json`, per-URL logs, and `failed.txt`, which can be passed back with `--batch` to retry failures.

Completion history is separated by output format, so rerunning the same list skips completed items. If an audio file was deleted but remains in history, use `--no-archive`. Do not run two processes against the same output directory.

## Development checks

```bash
python3 -m unittest discover -s tests -v
.venv/bin/python tests/smoke_local.py
```

The smoke test synthesizes local media with FFmpeg and downloads it from a temporary `127.0.0.1` server. It does not access a media platform.
