#!/usr/bin/env bash

set -euo pipefail

BASE="/home/ubuntu/mpp-tools" # Update this variable to match your installation path

echo "🔎 === Setup started ==="

check_directory() {
    local DIR="$1"

    if [ ! -d "$DIR" ]; then
        echo "❌ Directory does not exist: $DIR"
        exit 1
    fi
}

setup_python_env() {
    local APP_DIR="$1"

    echo ""
    echo "🏗️ === Setup $(basename "$APP_DIR") ==="

    check_directory "$APP_DIR"

    cd "$APP_DIR"

    # Create virtual environment only if missing
    if [ ! -d "venv" ]; then
        echo "🐍 Creating virtual environment..."
        python3 -m venv venv
    else
        echo "🐍 Virtual environment already exists. Skipping creation."
    fi

    echo "⚡ Activating virtual environment..."
    source venv/bin/activate

    echo "📦 Checking dependencies..."

    # Upgrade pip only if needed
    python -m pip install --quiet --upgrade pip

    # Install/update dependencies
    if [ -f "requirements.txt" ]; then
        python -m pip install --quiet -r requirements.txt
    else
        echo "ℹ️ No requirements.txt found in $APP_DIR"
    fi

    deactivate

    echo "✅ $(basename "$APP_DIR") setup completed."
}


# Verify base directory
check_directory "$BASE"


# Setup applications
setup_python_env "$BASE/src/extract_data"
setup_python_env "$BASE/src/build_report"


# Permissions
echo ""
echo "🔐 Checking permissions..."

RUN_SCRIPT="$BASE/run.sh"

if [ -f "$RUN_SCRIPT" ]; then
    if [ ! -x "$RUN_SCRIPT" ]; then
        chmod +x "$RUN_SCRIPT"
        echo "✅ Added execute permission to run.sh"
    else
        echo "ℹ️ run.sh is already executable"
    fi
else
    echo "⚠️ run.sh not found, skipping chmod"
fi


echo ""
echo "🎉 === Installation completed successfully ==="
