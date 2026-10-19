#!/bin/sh
# Render tools/card-image/mazinah.html to a 1080x1350 PNG with headless Chrome.
# Usage: tools/card-image/render.sh [output.png]
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$DIR/mazinah-card.png}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1080,1350 --virtual-time-budget=8000 \
  --screenshot="$OUT" "file://$DIR/mazinah.html" >/dev/null 2>&1
echo "Wrote $OUT"
