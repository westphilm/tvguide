#!/usr/bin/env bash

## Start script for tvguide:
# nohup "$HOME/bin/tvguide.sh" </dev/null >"$HOME/tvguide.log" 2>&1 &

set -euo pipefail

cd /opt/tvguide
export TVGUIDE_HOST=0.0.0.0
exec /opt/tvguide/.venv/bin/python -m app.main
