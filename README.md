# 🔌 Clarity Grid Chatbot - Reduced Dataset Local Edition

## 📊 Dataset Overview
- **41,843 optimized US electrical transmission lines**
- **50% of full dataset** with high-priority lines only
- **Smart selection**: Prioritized by voltage, length, and operational status
- **Perfect for resource-constrained deployment**

## 🚀 Quick Start

### Windows
```bash
# Double-click to run
start.bat

# Or run manually
python -m uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

### Access the Application
- **Web Interface**: http://localhost:8002
- **Health Check**: http://localhost:8002/health
- **Dataset Info**: http://localhost:8002/info

## 📁 Required Files
This folder contains:
- ✅ `app.py` - Simplified FastAPI application for reduced dataset
- ✅ `requirements.txt` - Python dependencies
- ✅ `templates/` - HTML templates folder
- ✅ `reduced_electrical_grid_index.faiss` - FAISS vector index (61MB)
- ✅ `reduced_electrical_grid_metadata.json` - Line metadata (25MB)
- ✅ `start.bat` - Windows startup script

## 🎯 Optimization Strategy
The reduced dataset includes:
- **All 500kV+ transmission lines** (highest priority infrastructure)
- **Major metropolitan area infrastructure**
- **Interstate transmission connections**
- **Critical grid backbone components**
- **Longest transmission lines** (high importance)
- **Lines with "IN SERVICE" status** (operational priority)

## 🔧 System Requirements
- **Python 3.8+**
- **2GB+ RAM** (lighter than full dataset)
- **100MB+ disk space** for dataset files
- **Internet connection** for initial package installation

## 📈 Performance Comparison

| Metric | Reduced Dataset (Port 8002) | Full Dataset (Port 8001) |
|--------|------------------------------|---------------------------|
| **Lines** | 41,843 | 83,686 |
| **FAISS Size** | 61MB | 123MB |
| **Metadata Size** | 25MB | 56MB |
| **RAM Usage** | ~100MB | ~180MB |
| **Query Speed** | <1.5 seconds | <2 seconds |
| **Coverage** | High-priority lines | Complete coverage |

## 💡 Usage Examples
Perfect for queries about major infrastructure:
- "Find 765kV transmission lines"
- "Show me interstate connections"
- "What are the major transmission corridors?"
- "Find lines connecting major cities"

## 🛠️ When to Use This Version
- **Demos and presentations** - faster loading
- **Resource-constrained environments** - lower memory usage
- **Cloud deployment** - fits free tier limits
- **Development testing** - quicker iteration

---

**Built with**: FastAPI + FAISS + Sentence Transformers + Google Gemini AI  
**Dataset**: 41,843 high-priority US electrical transmission lines  
**Cost**: $0 ongoing (free embedding model + local deployment)