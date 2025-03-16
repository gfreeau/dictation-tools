#!/bin/bash

# Get script directory
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Find the nerd-dictation process
DICTATION_PID=$(pgrep -f "python3.*nerd-dictation.*begin")

if [ -z "$DICTATION_PID" ]; then
    echo "Error: Could not find nerd-dictation process."
    echo "Please run init-dictation.sh first to start the dictation system."
    exit 1
fi

echo "Monitoring nerd-dictation process (PID: $DICTATION_PID)..."
echo "Waiting for speech model to load and initialize..."

# Function to display a desktop notification
show_notification() {
    if command -v notify-send &> /dev/null; then
        notify-send -t 5000 "$1" "$2"
    fi
}

# Monitor the process status
MAX_WAIT=60  # Maximum wait time in seconds
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # Check if the process is still running
    if ! ps -p $DICTATION_PID > /dev/null; then
        echo "Error: Speech recognition process terminated unexpectedly."
        exit 1
    fi
    
    # Check if the process status is 'T' (stopped)
    PROCESS_STATUS=$(ps -o stat= -p $DICTATION_PID)
    if [[ $PROCESS_STATUS == T* ]]; then
        echo "-------------------------------------------------------------"
        echo "✓ Speech recognition system initialized and ready!"
        echo "• To start dictating: run ./start-dictation.sh"
        echo "• To stop dictating: run ./stop-dictation.sh"
        echo "-------------------------------------------------------------"
        
        # Show success notification
        show_notification "Speech Recognition Ready" "Speech model loaded successfully. Run start-dictation.sh to begin."
        exit 0
    fi
    
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
    
    # Show progress every 5 seconds
    if [ $((WAIT_COUNT % 5)) -eq 0 ]; then
        echo "Still loading speech model... ($WAIT_COUNT seconds)"
    fi
done

echo "Warning: Timed out waiting for initialization to complete."
echo "The system may still be loading. Current process status: $PROCESS_STATUS"
exit 1 