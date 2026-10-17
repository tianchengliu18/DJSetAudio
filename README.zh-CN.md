# DJSetAudio

[English](README.en.md) | 简体中文

**把一批视频或音频链接放进 TXT，一次运行，批量下载并提取音轨。**

将有权下载的链接逐行写入 `urls.txt`，运行一个命令，即可在 `audio/` 中获得可直接使用的音频文件。

`urls.txt` → 并发下载 → FFmpeg 提取音轨 → MP3、M4A、FLAC 或来源音质

- 支持 macOS 和 Windows，全部在本机运行。
- 默认同时下载 3 条链接，每个任务使用固定行动态显示进度。
- 自动记录已完成项目，支持来源允许的断点续传，并生成失败重试清单。

主流程使用 **yt-dlp + FFmpeg**，不需要把链接清单上传到解析网站。它提取整段音轨，不识别曲目、不拆分人声或鼓点，也不保证所有平台链接均可解析。只处理你有权下载的内容，不提供绕过 DRM、付费或访问权限的功能。

## 1. 第一次安装

先把整个项目文件夹解压或保存到固定位置。下面的安装命令会访问软件源；安装脚本只创建项目的 `.venv`，不会安装 DJ Tools 或修改系统 Python。

### macOS

打开「终端」。如果已有 [Homebrew](https://brew.sh/)，安装 Python、FFmpeg 和 Deno：

```bash
brew install python ffmpeg deno
cd "/你的路径/DJSetAudio"
bash scripts/setup-macos.sh
bash run.sh --doctor
```

没有 Homebrew 时，按其官网说明安装并完成页面提示的 PATH 设置；也可以从 [Python 官网](https://www.python.org/downloads/macos/)、[FFmpeg 下载页](https://ffmpeg.org/download.html)及 [Deno 安装页](https://docs.deno.com/runtime/getting_started/installation/)分别安装。FFmpeg 下载页链接到第三方编译版本，需同时取得 `ffmpeg` 和 `ffprobe` 可执行文件；不是 `pip install ffmpeg`。

安装完成后，后续只需编辑 TXT 并运行：

```bash
bash run.sh
```

也可以在 Finder 双击 `Start.command`。若系统不允许执行，先运行 `chmod +x Start.command`；系统提示来源不明时按 macOS 的正常文件审核流程处理。更换项目位置后重新运行安装脚本；不要复制别台机器的 `.venv`。

### Windows 10/11

1. 从 [Python 官网](https://www.python.org/downloads/windows/)安装 Python，建议 3.12 或更新版本；最低 3.10。安装器若提供 `Add Python to PATH`，请勾选。
2. 打开 PowerShell，安装 FFmpeg 和 Deno：

```powershell
winget install --exact --id Gyan.FFmpeg --source winget
winget install --exact --id DenoLand.Deno --source winget
```

关闭并重新打开 PowerShell，使新的 PATH 生效。进入你自己的项目目录（下面是示例位置，请替换）：

```powershell
cd "C:\Users\你的用户名\Projects\DJSetAudio"
.\scripts\setup-windows.ps1
.\run.ps1 --doctor
```

若提示不允许运行 PowerShell 脚本，只对当前窗口设置，然后重新运行上面的安装脚本：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

若下载文件仍带有网络来源标记，审阅项目脚本后用 `Unblock-File .\scripts\setup-windows.ps1` 和 `Unblock-File .\run.ps1` 解除这两个文件的标记。公司策略禁止脚本时，联系管理员或使用下方的手动安装命令。

后续可双击 `Start.cmd`，也可运行：

```powershell
.\run.ps1
```

没有 winget 时，从 [FFmpeg 官方下载入口](https://ffmpeg.org/download.html)选择 Windows 构建，把其中 `bin` 目录加入 PATH；Deno 按其[官方安装说明](https://docs.deno.com/runtime/getting_started/installation/)安装。Windows ARM 电脑需选适配架构的构建。安装后分别检查 `ffmpeg -version`、`ffprobe -version`、`deno --version`。

### 安装脚本做了什么

创建 `.venv`，用 `pip install --upgrade --pre -r requirements.txt` 安装 `yt-dlp[default]`，记录实际依赖到 `installed-versions.txt`，最后检查本地工具。这里跟随官方建议使用 nightly，因平台接口会变化；这不是固定版本保证。需要稳定版时可手动使用 `pip install --upgrade "yt-dlp[default]"`；从较新 nightly 回退到稳定版应增加 `--force-reinstall`。

Python 3.10+ 是当前 yt-dlp 和 DJ Tools 包的最低要求；旧 DJ Tools 开发文档中的 Python 3.9 已与当前包元数据不同。[DJ Tools 包元数据](https://pypi.org/project/djtools/)、[yt-dlp 安装说明](https://github.com/yt-dlp/yt-dlp/wiki/Installation)供核对。

YouTube 完整支持还需要匹配的 EJS 组件和 JavaScript 环境。本项目通过 `[default]` 一并安装 EJS，优先使用 PATH 中的 Deno，没有时选择 Node；截至核实日最低要求 Deno 2.3.0 或 Node 22.0.0。也可以显式加 `--js-runtime node` 或 `--js-runtime deno`。脚本选择可执行程序后，由 yt-dlp 判断版本是否受支持。无需自行启用远程脚本下载。依据：[官方 EJS 设置说明](https://github.com/yt-dlp/yt-dlp/wiki/EJS)。

## 2. 每行一个 URL

用记事本、VS Code 等编辑项目内 `urls.txt`。Mac「文本编辑」须切换为「纯文本」，不要保存为 RTF。使用 UTF-8 编码，Windows 的 UTF-8 BOM 也支持。

```text
# 下面仅展示格式，请替换成你有权下载的真实地址
https://example.com/my-authorized-set-1.mp4
https://example.com/my-authorized-set-2.mp3
```

示例域名不会提供测试录音。清单中每行只放网址，不要加引号、序号或行尾备注；保留链接中的 `?`、`&`、`#`。空行及 `#` 开头的整行忽略，同一完整 URL 去重。发现格式错误会报告行号并在下载前停止，修正后重跑即可。

默认读取项目内 `urls.txt`，无论从哪个文件夹启动。指定其他 TXT 时，相对路径按当前终端目录解释，带空格的路径加引号。

## 3. 先预览，再开始

macOS：

```bash
bash run.sh --dry-run
bash run.sh --simulate
bash run.sh
```

Windows PowerShell：

```powershell
.\run.ps1 --dry-run
.\run.ps1 --simulate
.\run.ps1
```

`--dry-run` 只检查清单并显示参数，不联网，也不写文件。`--simulate` 会联网读取元数据、不下载媒体、不更新完成历史；本项目仍会写诊断日志和结果报告。模拟成功不能保证稍后实际下载或转码成功。

你也可以直接运行 Python 核心：macOS 用 `.venv/bin/python extract_audio.py`，Windows 用 `.venv\Scripts\python.exe extract_audio.py`，后面参数完全相同。

## 4. 常用操作

| 需求 | 给运行命令追加的参数 |
| --- | --- |
| 读取别处的 TXT | `--batch "路径/我的链接.txt"` |
| 导出 MP3 | `--format mp3` |
| 导出 M4A | `--format m4a` |
| 导出 FLAC | `--format flac` |
| 修改保存位置 | `--output "路径/DJMusic"` |
| 修改同时下载数 | `--jobs 5`（允许 1–16，默认 3） |
| 切换界面语言 | `--language en` 或 `--language zh` |
| 只试一条 | `"https://example.com/your-authorized-file.mp4"` |
| FFmpeg 不在 PATH | `--ffmpeg-location "同时包含两个工具的目录"` |
| 已删除音频，要补下 | `--no-archive` |
| 显示诊断 | `--verbose` |

例如 Mac 使用另一份 TXT，全部转 MP3：

```bash
bash run.sh --batch "/你的路径/我的DJ链接.txt" --format mp3
```

Windows 示例：

```powershell
.\run.ps1 --batch "D:\DJ\我的链接.txt" --output "D:\DJMusic" --format mp3
```

默认会并发处理 3 条链接。交互式终端为每个正在下载的任务保留一行，百分比、速度和 ETA 会在原位置刷新，不会为每次进度变化新增一行；开始、完成、警告和转码等事件仍正常换行。非交互式输出会省略高频进度，详细原始输出分别保存在任务日志中。网络较慢且来源允许时可以适当提高 `--jobs`；遇到平台限速、429 错误、机器转码负载过高或希望逐条排查时，改用 `--jobs 1`。这是单机并发，不会把链接发送给其他电脑或服务。

默认 `best` 尽量保留来源音频编码，可能输出 Opus、M4A 等；并不固定为 MP3。MP3 使用高质量 VBR，具体码率取决于编码器和音频，不能承诺固定 320 kbps。FLAC 只是无损保存解码后的声音，不能让有损来源恢复音质。选择 `bestaudio/best` 会优先音频流，若只有带音视频的文件，则需下载它再提取音轨。[相关格式选项](https://github.com/yt-dlp/yt-dlp#format-selection)。

需要复现本次验证环境时，可在隔离环境安装 `requirements-tested.txt` 中的版本；它是 macOS/Python 3.13 的记录，不替代日常更新策略或 Windows 实机测试。

## 5. 重跑、失败和保存位置

```text
DJSetAudio/
  urls.txt
  audio/
    best/ 或 mp3/、m4a/、flac/     音频
    .dj-work/
      archive-best.txt             按输出格式区分的完成历史
      runs/日期时间-随机后缀/
        results.json              每条 URL 的结果、文件路径、退出码
        failed.txt                本次失败 URL，可直接作为下一次输入
        0001.log                  各链接的详细输出
```

单条失败后继续下一条。汇总中 `completed` 表示 yt-dlp 返回成功且回报的输出文件存在；`parsed` 是模拟解析成功；`skipped_or_no_output` 通常表示已在完成历史中，也可能是平台未返回媒体，需要查看对应日志；`failed` 表示非零退出或缺失输出。退出码 0 表示没有记录到失败（可能全部跳过），1 表示有失败，2 表示输入/依赖错误，130 表示手动中断。

完成历史按保存目录和格式分开，重新运行同一 TXT 会跳过已完成项。改变格式可再次提取到另一个格式目录。支持来源允许情况下的 `.part` 续传；不是所有传输都支持断点恢复。默认不覆盖已有输出；失败的后处理不会被本项目主动写入完成历史，完成记录由 yt-dlp 管理。

直接把 `failed.txt` 的完整路径交给 `--batch` 可重试。中断时正在处理和未开始的 URL 不会被写进 `failed.txt`；重新跑原 TXT 才能覆盖这些链接。不要同时向同一输出目录运行两个任务；遇到遗留的 `run.lock`，先确认进程已停止，再删除这个锁文件。

误删音频后，历史仍会跳过它：用 `--no-archive` 恢复，或者针对性编辑历史。它不会覆盖已有文件；损坏但已存在的文件应先移走再重试。日志、报告和 TXT 可能含私人网址或临时令牌，分享前检查内容。

每条输入以单条媒体为用途，关联播放列表时优先当前视频；独立列表链接最多取第一项。请把想处理的各条演出 URL 分别写进 TXT，别用播放列表 URL 代替清单。直播进行中时请等归档后再处理。

## 6. 更新与排查

每次遇到网站解析变化，先重跑对应系统的 setup 脚本更新隔离环境。不要混用系统的旧 `yt-dlp` 与项目 `.venv` 的版本；`--doctor` 会显示实际使用情况。Homebrew 的 FFmpeg/Deno 用 `brew upgrade ffmpeg deno` 更新；Windows 对应使用 `winget upgrade --exact --id Gyan.FFmpeg` 和 `winget upgrade --exact --id DenoLand.Deno`。

详细报错说明见 [故障排查](docs/TROUBLESHOOTING.md)。DJ Tools 原命令、现版差异与隔离安装见 [DJ Tools 教程](docs/DJ_TOOLS.md)。官方来源与验证边界见 [核实记录](docs/SOURCES.md) 和 [验证报告](docs/VALIDATION.md)。

## 7. 手动安装与开发验证

不使用安装脚本时，macOS：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade --pre "yt-dlp[default]"
```

Windows（PowerShell/CMD 均可）：

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade --pre "yt-dlp[default]"
```

FFmpeg、ffprobe、Deno 仍需单独安装。脚本不要求激活虚拟环境。虚拟环境失败时检查 Python 是否带 `venv`，不要使用 `sudo pip` 或强行覆盖受管理的 Python 环境。

核心验证无需额外测试库：

```bash
python3 -m unittest discover -s tests -v
```

可选端到端验证会合成本地测试音视频，在 `127.0.0.1` 临时提供文件，通过真实 yt-dlp/FFmpeg 执行下载提取及重复跳过；不访问演出平台：

```bash
.venv/bin/python tests/smoke_local.py
```

Windows 将上述 Python 路径替换为 `.venv\Scripts\python.exe`。此验证不等于任一商业平台或具体 DJ Set 下载成功。
