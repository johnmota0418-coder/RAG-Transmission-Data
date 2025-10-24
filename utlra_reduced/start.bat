@echo off
REM Start script for reduced transmission lines RAG app

echo 🚀 Starting Reduced Transmission Lines RAG Application...
echo 📊 This version uses ~50%% of the full dataset for faster performance

REM Install dependencies
pip install -r requirements.txt

REM Start the application
python app.py

pause