#!/bin/sh
if ! command -v python3 &> /dev/null
then
    echo "Python is not installed."
    exit 1
fi

pip install -r ./requirements.txt

python -m uvicorn apps.main:app --host 0.0.0.0 --port 8000