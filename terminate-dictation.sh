#!/bin/bash

# Find and kill any running nerd-dictation processes
pkill -f "nerd-dictation"

# Force kill any stubborn processes
pkill -9 -f "nerd-dictation"

# Kill any stopped processes
for pid in $(ps aux | grep "nerd-dictation" | grep -v grep | awk '{print $2}'); do
    echo "Killing process $pid"
    kill -9 $pid 2>/dev/null
done

echo "All dictation processes terminated." 