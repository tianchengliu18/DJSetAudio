#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="$project_dir/.venv/bin/python"
if [[ ! -x "$python_bin" ]]; then python_bin="${DJ_PYTHON:-python3}"; fi
exec "$python_bin" "$project_dir/extract_audio.py" "$@"
