#!/usr/bin/env bash
set -euo pipefail
DSS_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v "${DSS_PYTHON:-python3}" >/dev/null 2>&1; then
    echo "Python 3.11+ is required. See README.md -> Linux." >&2
    exit 1
fi
exec "${DSS_PYTHON:-python3}" "$DSS_ROOT/tools/launch_linux.py" "$@"
