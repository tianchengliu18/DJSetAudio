# DJ Tools 原教程：先修正现版命令

核实日：2026-10-17。DJ Tools 2.9.1 于 2026-07-04 发布，不能称为停止维护。但这个 URL 提取功能仍封装 `youtube-dl`；本项目的 TXT 批量入口使用 yt-dlp。依据：[PyPI](https://pypi.org/project/djtools/)、[当前依赖定义](https://github.com/a-rich/DJ-Tools/blob/main/pyproject.toml)。

## 官方网页的旧示例

[用户提供的网页](https://a-rich.github.io/DJ-Tools-dev-docs/how_to_guides/extract_from_url/)确实写着：

```text
djtools --url-download <URL> --url-download-destination <PATH>
```

但当前 2.9.1 仓库的[命令行定义](https://github.com/a-rich/DJ-Tools/blob/main/src/djtools/configs/cli_args.py)已使用 `utils` 子命令，保存目录参数叫 `--audio-destination`。所以不要直接复制旧网页命令到现版。

按当前参数定义应写为：

```text
djtools utils --url-download "你的授权媒体URL" --audio-destination "专用空目录" --audio-format mp3 --audio-bitrate 320
```

其中 `--url-download` 指定一条 URL，`--audio-destination` 是本地保存目录，后两项指定输出格式和码率。码率设置不能提高原始音源质量。运行前先用 `djtools utils --help` 核对你安装版本的参数。

本项目从官方参数源文件构建解析器，验证了上述新参数能被接受、旧示例会被拒绝。这个检查只覆盖参数解析，未运行 DJ Tools 完整下载流程，不能证明其后端目前支持某个演出链接。

## macOS：单独隔离安装

建议用 Python 3.12，当前 DJ Tools 的分类声明包含 3.10–3.12；较新 Python 的兼容性应实际检查，不能把 3.10+ 解读为每个未来版本都已测试。尤其旧音频依赖可能在 Python 3.13+ 遇到 `audioop` 相关导入错误。

在项目文件夹里运行（先确保 Python 3.12 与 FFmpeg 已安装；Homebrew 可 `brew install python@3.12 ffmpeg`）：

```bash
python3.12 -m venv .venv-djtools
.venv-djtools/bin/python -m pip install --upgrade pip
.venv-djtools/bin/python -m pip install "djtools==2.9.1"
.venv-djtools/bin/djtools --version
.venv-djtools/bin/djtools utils --help
mkdir -p audio/djtools-new
.venv-djtools/bin/djtools utils --url-download "https://example.com/your-authorized-set.mp4" --audio-destination "$PWD/audio/djtools-new" --audio-format mp3 --audio-bitrate 320
```

示例 URL 需替换。不要把 `.venv-djtools` 和主流程的 `.venv` 混用；不需要安装 accelerated 扩展。

## Windows：单独隔离安装

从 Python 官网安装 Python 3.12 并确保 FFmpeg/ffprobe 在 PATH；然后在 PowerShell 中：

```powershell
py -3.12 -m venv .venv-djtools
.venv-djtools\Scripts\python.exe -m pip install --upgrade pip
.venv-djtools\Scripts\python.exe -m pip install "djtools==2.9.1"
.venv-djtools\Scripts\djtools.exe --version
.venv-djtools\Scripts\djtools.exe utils --help
New-Item -ItemType Directory -Path ".\audio\djtools-new" -Force
.venv-djtools\Scripts\djtools.exe utils --url-download "https://example.com/your-authorized-set.mp4" --audio-destination "$PWD\audio\djtools-new" --audio-format mp3 --audio-bitrate 320
```

## 使用边界

从[当前 URL 下载器源码](https://github.com/a-rich/DJ-Tools/blob/main/src/djtools/utils/url_download.py)可见，它通过 FFmpeg 后处理，并在下载后遍历保存目录重命名文件。因此每次试用应选择专门的空目录，不要指向已有音乐库。仅使用 URL 提取不需要为其 Spotify、Reddit、AWS 功能配置账号。

如果安装失败，先检查所用 Python 和依赖版本；如果报签名解析、平台拒绝或不支持链接，优先回到本项目 yt-dlp 主流程。不要通过简单卸载 youtube-dl、换装 yt-dlp 来假定兼容：当前源码显式导入的是 `youtube_dl`，二者不是同名替换包。

不提供把旧网页命令批量套用到 TXT 的入口，因为这会延续已核实的参数错误。实际批量使用直接编辑项目 `urls.txt`，运行 `bash run.sh` 或 `.\run.ps1`。
