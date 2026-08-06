#!/bin/bash

# =================================================
# How to use:
# =================================================
# 
# chmod +x run.sh
# crontab -e
# Add the following line:
# 0 10,14,20 * * * /home/ubuntu/mpp-tools/run.sh
# 
# =================================================

BASE="/home/ubuntu/mpp-tools"

(
    cd "$BASE" || exit 1

    SRC="$BASE/src"
    LOG="$BASE/logs"

    mkdir -p "$LOG"

    "$SRC/extract_data/venv/bin/python" "$SRC/extract_data/main.py" >> "$LOG/extract_data-log.txt" 2>&1 || exit 1
    "$SRC/build_html_report/venv/bin/python" "$SRC/build_html_report/main.py" >> "$LOG/build_html_report-log.txt" 2>&1
    "$SRC/build_md_report/venv/bin/python" "$SRC/build_md_report/main.py" >> "$LOG/build_md_report-log.txt" 2>&1
)
