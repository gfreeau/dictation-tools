#!/usr/bin/env bash
# Thin wrapper that starts Whisper-based dictation (see whisper_dictation.py)

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
python3 "$SCRIPT_DIR/whisper_dictation.py" start & 