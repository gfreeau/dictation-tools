#!/bin/bash

# Get script directory and source config
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CONFIG_FILE="$SCRIPT_DIR/dictation.conf"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

source "$CONFIG_FILE"

# Create log directory in the current script directory
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Generate timestamp for log filename
TIMESTAMP=$(date +"%Y%m%d")
LOG_FILE="$LOG_DIR/dictation_$TIMESTAMP.log"

# Check if xdotool is installed
if ! command -v xdotool &> /dev/null; then
    echo "Error: xdotool is not installed. Please install it with your package manager." | tee -a "$LOG_FILE"
    echo "For example: sudo apt install xdotool" | tee -a "$LOG_FILE"
    exit 1
fi

# Change to nerd-dictation directory
cd "$(dirname "$NERD_DICTATION_PATH")"
NERD_DICTATION="./$(basename "$NERD_DICTATION_PATH")"

$NERD_DICTATION begin \
  --vosk-model-dir="$VOSK_MODEL_DIR" \
  --full-sentence \
  --numbers-as-digits \
  --numbers-use-separator \
  --numbers-min-value=2 \
  --punctuate-from-previous-timeout=0 \
  --verbose=2 \
  --suspend-on-start > "$LOG_FILE" 2>&1 &

# Log the PID but don't store it in a file since we can detect it automatically
DICTATION_PID=$!
echo "Nerd-dictation started with PID: $DICTATION_PID" | tee -a "$LOG_FILE"

echo "Dictation process started. Speech model is now loading..."
echo "Check logs at: $LOG_FILE"
echo ""
echo "IMPORTANT: For large models, the initialization may take time."
echo "To monitor when the speech model is fully loaded, run:"
echo "  ./check-dictation-ready.sh"
echo ""
echo "Once the model is loaded, use start-dictation.sh to begin dictating." 