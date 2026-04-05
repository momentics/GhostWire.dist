#!/usr/bin/env sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <version> <asset-file>" >&2
  exit 1
fi

VERSION="$1"
ASSET="$2"
BASE_URL="https://github.com/momentics/GhostWire.dist/releases/download/${VERSION}"

echo "Fetching ${ASSET} from ${BASE_URL}"
curl -fL "${BASE_URL}/${ASSET}" -o "${ASSET}"
