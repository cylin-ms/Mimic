#!/bin/bash
# Wrapper to run the estimator in the isolated environment

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if venv exists
if [ ! -d "$DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate venv and run
source "$DIR/venv/bin/activate"
python "$DIR/estimate_value.py" "$@"
