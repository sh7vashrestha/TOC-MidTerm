#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 main.py --output outputs/main
python3 main.py --demo --output outputs/demo
