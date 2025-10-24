@echo off
REM Start script for ultra-reduced transmission lines RAG app with Azure Blob Storage

echo 🚀 Starting Ultra-Reduced Transmission Lines RAG Application...
echo 📊 This version loads data from Azure Blob Storage for minimal deployment size
echo 🌩️ Data files (~36MB) will be downloaded on first request

REM Install dependencies
pip install -r requirements.txt

REM Start the application
python -m uvicorn app_ultra:app --host 0.0.0.0 --port 8000

pause