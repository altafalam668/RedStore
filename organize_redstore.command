#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 organize_redstore.py
echo
echo "Finished. Press Enter to close."
read
