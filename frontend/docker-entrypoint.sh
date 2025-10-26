#!/bin/sh
set -e

# Check if node_modules is empty or doesn't exist
if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules 2>/dev/null)" ]; then
  echo "node_modules is empty, running npm install..."
  npm install
else
  echo "node_modules exists, skipping npm install"
fi

# Execute the CMD from Dockerfile
exec "$@"

