#!/usr/bin/env bash
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
bash "$project_dir/run.sh" "$@"
result=$?
language="$(tr -d '[:space:]' < "$project_dir/language.txt" 2>/dev/null || true)"
if [[ "$language" == "zh" ]]; then
    printf '\n退出码：%s（0=无失败，1=部分失败，2=输入或环境错误）\n' "$result"
    read -r -p '按回车键关闭窗口…' _
else
    printf '\nExit code: %s (0=no failures, 1=partial failure, 2=input or environment error)\n' "$result"
    read -r -p 'Press Enter to close…' _
fi
exit "$result"
