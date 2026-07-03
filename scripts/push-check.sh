#!/usr/bin/env bash
# 公开仓推送前白名单检查：仅允许列出的路径进入 commit
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ALLOWED=(
  '.gitignore'
  'LICENSE'
  'README.md'
  'README.gitee.md'
  'analyze_lhb.py'
  'config.example.yaml'
  'requirements.txt'
  'scripts/push-check.sh'
  'scripts/render_demo_png.py'
)

allowed_path() {
  local f="$1"
  for a in "${ALLOWED[@]}"; do
    [[ "$f" == "$a" ]] && return 0
  done
  [[ "$f" == assets/* ]] && return 0
  [[ "$f" == scripts/* ]] && return 0
  return 1
}

# staged + unstaged against HEAD (if any)
mapfile -t CHANGED < <(
  {
    git diff --name-only
    git diff --cached --name-only
    git ls-files --others --exclude-standard
  } | sort -u
)

if [[ ${#CHANGED[@]} -eq 0 ]]; then
  echo "OK: 无待推送变更"
  exit 0
fi

BAD=()
for f in "${CHANGED[@]}"; do
  [[ -z "$f" ]] && continue
  allowed_path "$f" || BAD+=("$f")
done

if [[ ${#BAD[@]} -gt 0 ]]; then
  echo "拒绝推送：以下文件不在公开仓白名单内：" >&2
  printf '  - %s\n' "${BAD[@]}" >&2
  echo >&2
  echo "白名单：README* / 代码 / assets / LICENSE / config.example.yaml / scripts/" >&2
  echo "永久禁止：方案与思路.md / config.yaml / docs/ / .env" >&2
  exit 1
fi

echo "OK: 变更均在白名单内（${#CHANGED[@]} 个文件）"
