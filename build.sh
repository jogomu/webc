#!/usr/bin/env bash
# Build the project tool image.
set -euo pipefail
cd "$(dirname "$0")"
docker build -t webc-tools .
