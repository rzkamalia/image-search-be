#!/bin/bash

echo "Weaviate is ready. Running vectorize.py..."
python3 vectorize.py

echo "Starting main application..."
python3 main.py