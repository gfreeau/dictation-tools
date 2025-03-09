#!/bin/bash

# Get script directory and source config
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CONFIG_FILE="$SCRIPT_DIR/dictation.conf"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

# Use NERD_DICTATION_PATH from config
cd "$(dirname "$NERD_DICTATION_PATH")"
NERD_DICTATION="./$(basename "$NERD_DICTATION_PATH")"

# Create log directory if it doesn't exist
LOG_DIR="$(dirname "$NERD_DICTATION_PATH")/logs"
mkdir -p "$LOG_DIR"

# Generate timestamp for log filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/dictation_$TIMESTAMP.log"

# Check if xdotool is installed
if ! command -v xdotool &> /dev/null; then
    echo "Error: xdotool is not installed. Please install it with your package manager." | tee -a "$LOG_FILE"
    echo "For example: sudo apt install xdotool" | tee -a "$LOG_FILE"
    exit 1
fi

$NERD_DICTATION begin \
  --vosk-model-dir="$VOSK_MODEL_DIR" \
  --full-sentence \
  --numbers-as-digits \
  --numbers-use-separator \
  --numbers-min-value=2 \
  --punctuate-from-previous-timeout=2.0 \
  --verbose=2 \
  --suspend-on-start > "$LOG_FILE" 2>&1 &

# Store the PID of the background process
DICTATION_PID=$!
echo "Nerd-dictation started with PID: $DICTATION_PID" | tee -a "$LOG_FILE"

echo "Dictation initialized and suspended. Use start-dictation.sh to start dictating." 