#!/usr/bin/env bash
set -euo pipefail

# The Python orchestrator enforces workers=4 from the tracked configuration.
exec "${PYTHON:-python3}" scripts/v007_full_repro.py "$@"
