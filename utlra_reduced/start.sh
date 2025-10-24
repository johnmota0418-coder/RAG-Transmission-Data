#!/bin/bash
# Start script for reduced transmission lines RAG app

echo "🚀 Starting Reduced Transmission Lines RAG Application..."
echo "📊 This version uses ~50% of the full dataset for faster performance"

# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py