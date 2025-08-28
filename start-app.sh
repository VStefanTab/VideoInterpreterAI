#!/bin/bash

# Script to start the VideoInterpreterAI application using docker-compose
# Usage: ./start-app.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting VideoInterpreterAI application..."
if docker compose up --remove-orphans -d; then
    echo "Application started successfully!"
    echo "Frontend available at: http://localhost:3000"
else
    echo "Failed to start application" >&2
    exit 1
fi