# 常见报错排查

先运行 `bash run.sh --doctor`（Mac）或 `.\run.ps1 --doctor`（Windows）。实际命令参数由当前官方 yt-dlp 支持；网站接口会改变，首先重跑项目的 setup 脚本更新。

| 现象 | 处理办法 |
| --- | --- |
| `python` / `py` / `python3` 找不到 | 安装 Python 3.10+，建议 3.12 或更新；Windows 检查 PATH/应用执行别名，重开终端。Mac 可给 setup 脚本设置 `DJ_PYTHON=/完整路径/python3`。 |
| `No module named yt_dlp` | 使用项目运行脚本，或明确用项目 `.venv` 内的 Python。重跑 setup；不要向另一套 Python 安装后混用。 |
| `externally-managed-environment` | 使用项目 `.venv`；不需要 `--break-system-packages`。 |
| `ffmpeg not found` / `ffprobe not found` | 安装可执行程序并重开终端。`pip install ffmpeg` 不会安装它们。也可以加 `--ffmpeg-location "bin目录"`，该目录需同时含两个程序。 |
| `No supported JavaScript runtime` / `n challenge solving failed` / 缺少 EJS | 安装或更新 Deno，确保在 PATH；同时重跑 setup 更新 `yt-dlp[default]`。若改用 Node，需 Node 22+ 并加 `--js-runtime node`。doctor 只显示可执行版本，最终是否符合要求以运行时 yt-dlp 诊断为准。 |
| `no such option: --js-runtimes` 等未知选项 | 当前用到了旧 yt-dlp。重跑 setup 后通过项目 `.venv` 启动；不要只更新系统安装。 |
| `HTTP Error 403` | 先更新、再确认源链接仍有效。直链签名可能过期，重新取得你有权访问的正式页面链接；也可能是服务器拒绝当前访问。不要反复重试失效签名链接。 |
| `HTTP Error 429` / 请求过多 | 停止任务，稍后再试，减少访问频率；本项目逐条执行，避免同时开多个任务。 |
| `Sign in to confirm` / private / members-only | 先确认网页访问状态和下载许可。公开链接也可能受平台验证影响。本项目不自动读取浏览器 Cookie，不请求账号密码。优先使用创作者提供的可下载源；权限或平台限制未解决时，记录该项失败。 |
| DRM / 付费 / 地区或权限限制 | 通过平台允许的下载方式或创作者授权文件取得音频；本项目不提供绕过方案。 |
| `Unsupported URL` | 确认是媒体页面或直接媒体文件 URL，不是搜索结果页。查阅 [yt-dlp 支持站点](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)；列入名单也不保证当前可用。 |
| `Requested format is not available` | 更新 yt-dlp，检查链接是否还有可用音轨；本项目已用 `bestaudio/best` 兼容独立音频与普通音视频。不要强行写死平台格式编号。 |
| 片段缺失 / fragment unavailable | 重跑原清单；本项目在片段失败时终止该条，避免默认跳过片段后误认为整段完整。成功重试取决于服务器是否仍提供素材。 |
| 下载完了但转码失败 | 检查 FFmpeg 版本、磁盘空间和编码器。先试 `--format best`。查看单条 `.log`；中间文件可能仍在格式目录，不要把中间视频当最终音轨。 |
| 中文 TXT 解码失败 | 用 UTF-8 另存为纯文本；不要用 GBK、UTF-16、RTF。UTF-8 BOM 已支持。 |
| 路径或清单不存在 | 带空格/中文的路径加引号，检查后缀是不是意外变成 `.txt.txt`。默认输入输出相对于项目，显式相对路径相对于当前终端。 |
| 文件名太长 / 无法写入 | 选短一些的输出目录。脚本已限制文件名并清理 Windows 不允许的字符，但完整路径仍受系统限制。 |
| 没声音 / 文件损坏 | 用 `ffprobe` 检查音频流；成功下载并不保证来源本身质量。移走损坏文件，再加 `--no-archive` 重试。 |
| 再跑后没下载 | 查看是否 `skipped_or_no_output` 和日志中的完成历史提示。误删音频后用 `--no-archive`；已有文件仍受不覆盖规则保护。 |
| 任务锁 `run.lock` 存在 | 先确认同一输出目录没有其他运行中的任务；异常退出后可删除 `audio/.dj-work/run.lock` 再重跑。不要删除活跃任务的锁。 |
| 占用磁盘较大 | 某些来源只有带视频文件，必须先下载再提取；转码时还需要临时空间。FLAC 也可能明显大于来源。 |
| 模拟成功但实际失败 | 模拟只检查元数据和格式解析；实际媒体请求、网络、磁盘和 FFmpeg 阶段仍可能失败，按日志排查。 |

需要诊断时加 `--verbose`，找到最新 `audio/.dj-work/runs/…/0001.log`。分享前检查网址令牌、用户名和本机路径。无需把 Cookie、密码或整份私人链接清单交给别人。

如果只想绕过 PowerShell 启动限制，可以在 PowerShell 或 CMD 直接调用 `.venv\Scripts\python.exe extract_audio.py`，不必修改长期执行策略。

离线复现检查：`python3 -m unittest discover -s tests -v`。本地工具链检查：项目 Python 运行 `tests/smoke_local.py`，仅使用本机合成素材。

参考：[yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ)、[EJS 设置](https://github.com/yt-dlp/yt-dlp/wiki/EJS)、[FFmpeg 官方下载入口](https://ffmpeg.org/download.html)。
