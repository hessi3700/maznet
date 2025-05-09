#!/bin/bash

# Navigate to the project directory
cd /workspaces/maznet || exit

# Add all changes to Git
if git diff-index --quiet HEAD --; then
  echo "No changes to commit."
else
  git add .

  # Commit changes with a timestamped message
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  git commit -m "Auto-commit: $TIMESTAMP"

  # Push changes to the remote repository
  git push origin main
fi
