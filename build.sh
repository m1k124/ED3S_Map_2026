#!/usr/bin/env bash
set -euo pipefail

pip install -r requirements.txt
python main.py
python scripts/check_build_output.py
