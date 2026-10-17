#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="${1:-$project_dir/dist}"
stage_dir="$(mktemp -d "${TMPDIR:-/tmp}/djsetaudio-release.XXXXXX")"
trap 'rm -rf "$stage_dir"' EXIT

mkdir -p "$output_dir"

copy_common_files() {
    local destination="$1"
    mkdir -p "$destination/audio"
    cp "$project_dir/.gitignore" "$destination/"
    cp "$project_dir/README.md" "$destination/"
    cp "$project_dir/README.en.md" "$destination/"
    cp "$project_dir/Start.cmd" "$destination/"
    cp "$project_dir/Start.command" "$destination/"
    cp "$project_dir/extract_audio.py" "$destination/"
    cp "$project_dir/requirements.txt" "$destination/"
    cp "$project_dir/requirements-tested.txt" "$destination/"
    cp "$project_dir/run.ps1" "$destination/"
    cp "$project_dir/run.sh" "$destination/"
    cp -R "$project_dir/docs" "$destination/"
    cp -R "$project_dir/scripts" "$destination/"
    cp -R "$project_dir/tests" "$destination/"
    find "$destination" -type d -name __pycache__ -prune -exec rm -rf {} +
    find "$destination" -type f -name '*.pyc' -delete
    : > "$destination/urls.txt"
    : > "$destination/audio/.gitkeep"
}

build_package() {
    local language="$1"
    local label="$2"
    local package_dir="$stage_dir/DJSetAudio-$label"
    local archive="$output_dir/DJSetAudio-$label.zip"

    copy_common_files "$package_dir"
    printf '%s\n' "$language" > "$package_dir/language.txt"
    if [[ "$language" == "en" ]]; then
        cp "$project_dir/README.md" "$package_dir/README.zh-CN.md"
        cp "$project_dir/README.en.md" "$package_dir/README.md"
        sed -i.bak 's#\[简体中文\](README.md)#[简体中文](README.zh-CN.md)#' "$package_dir/README.md"
        rm -f "$package_dir/README.md.bak"
    fi
    chmod +x "$package_dir/run.sh" "$package_dir/Start.command" \
        "$package_dir/scripts/setup-macos.sh" "$package_dir/scripts/build-release-packages.sh"
    test ! -s "$package_dir/urls.txt"
    test "$(find "$package_dir/audio" -type f ! -name .gitkeep | wc -l | tr -d ' ')" = "0"
    rm -f "$archive"
    (cd "$stage_dir" && COPYFILE_DISABLE=1 zip -qr "$archive" "DJSetAudio-$label")
    printf 'Built %s\n' "$archive"
}

build_package en English
build_package zh Chinese
