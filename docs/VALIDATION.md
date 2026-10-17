# 验证报告

日期：2026-10-17（Asia/Shanghai）。以下为实际核查与测试范围。

## 已核实的官方参数差异

核查 DJ Tools 官方仓库树 `5ff86b30e5588b7e511e559aafc308eaca6d2cbe`。以该版本的 `src/djtools/configs/cli_args.py` 构造 argparse 解析器（隔离了其音频配置枚举导入，未启动完整软件）：

- `utils --url-download … --audio-destination … --audio-format mp3 --audio-bitrate 320`：接受。
- 旧网页 `--url-download … --url-download-destination …`：拒绝，退出码 2。

完整 DJ Tools 包及其下载后端未运行；指南中的现版命令属于源码参数核实结果。

## 批量流程检查

`python3 -m unittest discover -s tests -v`：10 项通过，覆盖 UTF-8 BOM、空行与备注、URL 去重及片段保留、非法行阻止执行、无依赖离线预览、失败后继续及重试清单、任务锁、中断保存报告、默认多链接并发及结果顺序、交互式进度原位刷新、中英文界面、格式区分历史和模拟参数。

`bash -n`：Mac 三个入口脚本通过语法检查。全部 Python 文件通过 Python 3.10 语法兼容检查。

## 工具链与操作系统边界

真实本地合成素材测试 `tests/smoke_local.py`：通过 9 组检查，包括中文/空格路径和 BOM、重复链接去重、404 后继续、真实视频提取为 MP3、ffprobe 确认仅有音轨且时长约 2 秒、再次执行跳过且不改写输出、格式之间独立完成历史并提取 M4A、模拟不写媒体和完成历史。测试只在本机临时 HTTP 服务上读取 FFmpeg 合成的黑屏和正弦音视频，所有合成素材与临时输出在测试结束时清理。

实测环境：macOS x86_64，Python 3.13.7，FFmpeg/ffprobe 8.0，Node 22.15.0，yt-dlp CLI 报告 `2026.10.10.233141`（包版本 `2026.10.10.233141.dev0`），yt-dlp-ejs 0.8.0。`pip check` 通过。Deno 未安装，本次使用自动选中的 Node；没有执行 YouTube JS 解析，只验证了本地媒体流程。

验证环境精确依赖见 `requirements-tested.txt`。它记录本次环境，不承诺未来站点兼容；日常更新使用 setup 脚本。没有下载、解析或验证任何实际 DJ Set，也没有测试受限录音。

Windows PowerShell/CMD 入口已静态审阅，本次环境没有 PowerShell 或 Windows，未做 Windows 实机执行；Windows 步骤不能视作实机验证。YouTube 等平台的解析成功率没有实测。
