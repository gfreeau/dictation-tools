#!/bin/bash

# Get script directory and source config
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CONFIG_FILE="$SCRIPT_DIR/dictation.conf"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

cd "$(dirname "$NERD_DICTATION_PATH")"
NERD_DICTATION="./$(basename "$NERD_DICTATION_PATH")"

# Resume dictation
$NERD_DICTATION resume

# Set default message
MESSAGE="Speak naturally. Dictation is now inserting text."

# Add shortcut info to message if configured
if [[ -n "$STOP_DICTATION_KEY" ]]; then
    MESSAGE="$MESSAGE Press $STOP_DICTATION_KEY to end."
fi

# Display a notification
if command -v notify-send &> /dev/null; then
    notify-send -t 3000 "Dictation Active" "$MESSAGE"
fi

echo "Dictation started. Speak naturally. Use stop-dictation.sh to end." 