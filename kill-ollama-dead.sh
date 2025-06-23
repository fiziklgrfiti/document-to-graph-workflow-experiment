#!/bin/bash

# Script to find and kill all Ollama processes

echo "Finding all Ollama processes..."

# Find all processes with "ollama" in the name and store their PIDs
OLLAMA_PIDS=$(pgrep -f ollama)

# Check if any Ollama processes were found
if [ -z "$OLLAMA_PIDS" ]; then
  echo "No Ollama processes found."
  exit 0
fi

# Display the processes that will be killed
echo "Found the following Ollama processes:"
ps -f -p $OLLAMA_PIDS

# Ask for confirmation before killing
read -p "Do you want to kill these processes? (y/n): " CONFIRM

if [[ "$CONFIRM" == "y" || "$CONFIRM" == "Y" ]]; then
  # Kill all Ollama processes
  echo "Killing all Ollama processes..."
  kill $OLLAMA_PIDS
  
  # Wait a moment and check if they're really gone
  sleep 2
  REMAINING=$(pgrep -f ollama)
  
  if [ -z "$REMAINING" ]; then
    echo "All Ollama processes have been terminated successfully."
  else
    echo "Some processes are still running. Attempting to force kill..."
    kill -9 $REMAINING
    echo "Force kill completed."
  fi
else
  echo "Operation cancelled."
fi
