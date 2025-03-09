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

# End dictation (process text) and then suspend
$NERD_DICTATION suspend

# Set default message
MESSAGE="Dictation is now paused."

# Add shortcut info to message if configured
if [[ -n "$START_DICTATION_KEY" ]]; then
    MESSAGE="$MESSAGE Press $START_DICTATION_KEY to resume."
fi

# Display a notification
if command -v notify-send &> /dev/null; then
    notify-send -t 3000 "Dictation Stopped" "$MESSAGE"
fi

echo "Dictation is now paused. Use start-dictation.sh to resume dictating." 