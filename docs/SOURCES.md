# 官方核实记录

核实日期：2026-10-17（Asia/Shanghai）。本文件区分官网示例、包元数据和本项目实现判断。平台与依赖后续可能变化。

| 核实对象 | 结论与来源 |
| --- | --- |
| 用户给出的开发文档 | [extract_from_url](https://a-rich.github.io/DJ-Tools-dev-docs/how_to_guides/extract_from_url/) 确实展示 `djtools --url-download <URL> --url-download-destination <PATH>`，并称其封装 youtube-dl。 |
| 稳定版网站同页 | [稳定版教程](https://a-rich.github.io/DJ-Tools/how_to_guides/extract_from_url/) 也展示同一个示例；不能仅凭网页示例断言现版接受全部参数。 |
| DJ Tools 包 | [PyPI 页面](https://pypi.org/project/djtools/) 与 [PyPI JSON](https://pypi.org/pypi/djtools/json)：当前版本 2.9.1，2026-07-04 发布，Python >=3.10，仍依赖 youtube-dl。 |
| 旧安装指南 | [Setup](https://a-rich.github.io/DJ-Tools-dev-docs/tutorials/getting_started/setup/) 提到 Python 3.9 和 `pip install djtools`；当前包要求应按包元数据修正，accelerated 是可选项。 |
| 当前 DJ Tools 源码 | [pyproject.toml](https://github.com/a-rich/DJ-Tools/blob/main/pyproject.toml) 与 [URL 下载器](https://github.com/a-rich/DJ-Tools/blob/main/src/djtools/utils/url_download.py) 显示 Python >=3.10、youtube-dl、FFmpeg 后处理与 audio_destination 字段；下载后会遍历目标目录重命名文件。建议只用专门的空目录。 |
| 当前命令行参数 | [CLI 定义](https://github.com/a-rich/DJ-Tools/blob/main/src/djtools/configs/cli_args.py) 明确为 `djtools utils --url-download … --audio-destination …`；[UtilsConfig](https://github.com/a-rich/DJ-Tools/blob/main/src/djtools/utils/config.py) 与此对应。旧网页缺少子命令且保存路径参数不同。已用官方解析器源码进行隔离参数解析检查，详见 DJ_TOOLS.md。 |
| yt-dlp | [官方仓库](https://github.com/yt-dlp/yt-dlp)、[安装指南](https://github.com/yt-dlp/yt-dlp/wiki/Installation)：支持独立程序及 Python 包；本项目使用隔离 Python 包安装。依赖和各 CLI 参数以当前官方说明为准。 |
| YouTube 依赖 | [EJS 官方说明](https://github.com/yt-dlp/yt-dlp/wiki/EJS)：需要匹配的 EJS 和受支持的 JS 环境；`yt-dlp[default]` 带入配套 EJS，Deno 默认启用，Node 需显式启用。 |
| FFmpeg | [官方下载页](https://ffmpeg.org/download.html) 给出源代码及各平台外部编译包入口；需要 ffmpeg/ffprobe 二进制。 |
| macOS 软件包 | [Homebrew FFmpeg](https://formulae.brew.sh/formula/ffmpeg)、[Deno 官方安装指南](https://docs.deno.com/runtime/getting_started/installation/) 支持相应 brew 安装命令。 |
| Windows 软件包 | [Microsoft WinGet FFmpeg 清单](https://github.com/microsoft/winget-pkgs/tree/master/manifests/g/Gyan/FFmpeg) 确认 ID 为 Gyan.FFmpeg；[Deno 官方安装说明](https://docs.deno.com/runtime/getting_started/installation/) 提供 DenoLand.Deno。 |

**实现选择**：近期仍发布的 DJ Tools 不能称为已经停止维护。但其网址提取功能仍使用 youtube-dl，本项目因此直接采用 yt-dlp，减少对整套音乐库管理功能的依赖。这是基于来源作出的工程判断，不是对所有平台成功率的实测结论。

本项目只调用外部工具，不附带或改写第三方工具源码。各工具及构建的许可证按原项目适用。此次没有将真实 DJ Set 下载到交付文件中，也没有测试受限录音。
