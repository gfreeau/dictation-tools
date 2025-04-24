#!/usr/bin/env bash
# Thin wrapper that stops Whisper-based dictation and performs transcription

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
python3 "$SCRIPT_DIR/whisper_dictation.py" stop 