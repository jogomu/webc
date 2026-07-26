#!/usr/bin/env bash
# Interactive shell in the project tool image, repo mounted at /work.
set -euo pipefail
cd "$(dirname "$0")"
docker run --rm -it -v "$(pwd)":/work -w /work webc-tools /bin/bash
