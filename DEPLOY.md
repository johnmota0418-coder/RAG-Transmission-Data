# Deployment Guide for Reduced Transmission Lines RAG

## Ready-to-Deploy Package
This folder contains everything needed to deploy the reduced transmission lines RAG application.

## Contents
```
reduced_model_deploy/
├── app.py                                    # Main FastAPI application
├── reduced_electrical_grid_index.faiss      # FAISS vector index 
├── reduced_electrical_grid_metadata.json    # Metadata for 41,843 lines
├── requirements.txt                          # Dependencies
├── Dockerfile                               # Container config
├── start.sh                                 # Linux startup
├── start.bat                                # Windows startup
├── templates/index.html                     # Web UI
└── README.md                               # Documentation
```

## Quick Deploy Commands

### Local
```bash
cd reduced_model_deploy
pip install -r requirements.txt
python app.py
```

### Docker
```bash
cd reduced_model_deploy
docker build -t transmission-rag-reduced .
docker run -p 8002:8002 transmission-rag-reduced
```

### Cloud Platform
1. Upload this entire folder to your cloud platform
2. Set the start command to: `python app.py`
3. Ensure port 8002 is exposed

## Access
- Application: http://localhost:8002
- API: POST to http://localhost:8002 with JSON {"query": "your question"}

This optimized version uses 50% of the original dataset for faster performance!