#!/usr/bin/env bash
set -euo pipefail
DSS_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$DSS_ROOT/start.sh" --skip-install --service backend "$@"
