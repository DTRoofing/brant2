#!/bin/bash

# This script removes API keys from the specified files in git history

git filter-branch --force --index-filter '
  # Remove the files with secrets completely from history
  git rm --cached --ignore-unmatch build-documents/brant_optimized_env.sh
  git rm --cached --ignore-unmatch build-documents/cursor_one_liner.md
  git rm --cached --ignore-unmatch build-documents/scaffold_script.py
  git rm --cached --ignore-unmatch PROJECT_TAKEHOME.md
' --prune-empty --tag-name-filter cat -- --all

echo "Secrets removed from git history"