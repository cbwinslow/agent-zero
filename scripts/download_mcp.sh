#!/bin/bash
set -euo pipefail
URL="$1"
DEST="mcp_servers"
mkdir -p "$DEST"

if [[ "$URL" == *.git ]]; then
    git clone "$URL" "$DEST/$(basename "$URL" .git)" || {
        echo "Failed to clone $URL" >&2
        exit 1
    }
else
    filename=$(basename "$URL")
    curl -L "$URL" -o "$DEST/$filename" || {
        echo "Failed to download $URL" >&2
        exit 1
    }
fi

echo "MCP server downloaded to $DEST"
