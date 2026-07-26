#!/usr/bin/env bash
# Regenerate books/ from source/usfm/ inside the project tool image.
set -euo pipefail
cd "$(dirname "$0")"
docker run --rm -v "$(pwd)":/work -w /work webc-tools python3 tools/usfm2md.py
