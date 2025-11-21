#!/usr/bin/env bash
# Toggle dictation - starts recording if not active, stops and transcribes if active

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
"$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/whisper_dictation.py" toggle
