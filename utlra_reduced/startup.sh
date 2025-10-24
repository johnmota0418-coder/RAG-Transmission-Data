#!/bin/bash

# Azure App Service startup script for FastAPI application
echo "🚀 Starting RAG Transmission Data Application on Azure App Service..."
echo "📊 Loading from Azure Blob Storage for optimal performance"

# Install dependencies
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start the FastAPI application with uvicorn
echo "🌐 Starting FastAPI server..."
exec uvicorn app_ultra:app --host 0.0.0.0 --port $PORT