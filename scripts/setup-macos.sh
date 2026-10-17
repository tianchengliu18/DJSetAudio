#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${DJ_PYTHON:-python3}"
"$python_bin" -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ is required; Python 3.12 or newer is recommended"'
if [[ ! -x "$project_dir/.venv/bin/python" ]]; then
    "$python_bin" -m venv "$project_dir/.venv"
fi
"$project_dir/.venv/bin/python" -m pip install --upgrade pip
"$project_dir/.venv/bin/python" -m pip install --upgrade --pre -r "$project_dir/requirements.txt"
"$project_dir/.venv/bin/python" -m pip freeze > "$project_dir/installed-versions.txt"
"$project_dir/.venv/bin/python" "$project_dir/extract_audio.py" --doctor
