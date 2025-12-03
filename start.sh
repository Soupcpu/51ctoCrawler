#!/bin/bash

echo "========================================"
echo "51CTO Backend API"
echo "========================================"
echo ""

echo "Checking dependencies..."
python3 -c "import fastapi, uvicorn, selenium" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Dependencies not installed!"
    echo "Installing..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Starting server..."
python3 run.py
