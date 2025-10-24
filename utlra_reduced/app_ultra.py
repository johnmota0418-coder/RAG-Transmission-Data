from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import numpy as np
import google.generativeai as genai
import asyncio
import gc
import aiohttp
import tempfile

# We will lazy-load heavy ML libraries (faiss, sentence_transformers) when needed
# to reduce memory usage at startup on small hosts (e.g. Render free instances).

# Global semaphore to limit concurrent requests
request_semaphore = asyncio.Semaphore(2)  # Max 2 concurrent requests

app = FastAPI(title="Clarity Grid Chatbot - Ultra-Reduced Dataset (16,737 Lines) - Azure Blob Storage")

# Template directory configuration for Azure deployment
template_dir = os.path.join(os.path.dirname(__file__), "../templates")
if not os.path.exists(template_dir):
    # Fallback for Azure deployment where templates might be in same directory
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(template_dir):
        # Create a minimal templates directory if none exists
        os.makedirs(template_dir, exist_ok=True)

templates = Jinja2Templates(directory=template_dir)

# Configure Gemini AI
api_key = os.getenv("GOOGLE_AI_API_KEY")
if not api_key:
    print("❌ WARNING: GOOGLE_AI_API_KEY environment variable not set!")
    print("   Please set this in Azure App Service Configuration")
else:
    genai.configure(api_key=api_key)
    print("✅ Google AI API key configured successfully")

# Azure Blob Storage URLs for ultra-reduced dataset (16,737 records - 20% of original)
FAISS_INDEX_URL = "https://itse9cac.blob.core.windows.net/public/ultra_reduced_electrical_grid_index.faiss"
METADATA_URL = "https://itse9cac.blob.core.windows.net/public/ultra_reduced_electrical_grid_metadata.json"

# Temporary file paths (will be downloaded to temp directory)
FAISS_INDEX_PATH = None
METADATA_PATH = None

# We'll defer loading of the embedding model, FAISS index and metadata until
# they're required. This significantly reduces memory used during the build
# or initial startup on low-memory hosts.

# Globals populated by ensure_rag_loaded()
embedding_model = None
index = None
texts = []
RAG_AVAILABLE = False

async def download_file_from_url(url: str, local_path: str):
    """Download a file from URL to local temporary path with memory optimization"""
    print(f"📥 Downloading {url}...")
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status == 200:
                file_size = int(response.headers.get('content-length', 0))
                print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
                
                with open(local_path, 'wb') as f:
                    downloaded = 0
                    async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        if file_size > 0:
                            progress = (downloaded / file_size) * 100
                            if downloaded % (5 * 1024 * 1024) == 0:  # Log every 5MB
                                print(f"📥 Progress: {progress:.1f}% ({downloaded / (1024*1024):.1f}MB)")
                
                print(f"✅ Downloaded to {local_path}")
                return True
            else:
                print(f"❌ Failed to download {url}: HTTP {response.status}")
                return False

async def ensure_rag_loaded():
    """Load FAISS index, metadata, and embedding model on first use.
    Downloads files from Azure Blob Storage to temporary directory.

    This function imports heavy libraries locally to avoid loading them at
    process start. Call this in `retrieve_documents` before running searches.
    """
    global embedding_model, index, texts, RAG_AVAILABLE, FAISS_INDEX_PATH, METADATA_PATH
    if RAG_AVAILABLE:
        return

    try:
        print("📥 Lazy-loading embedding model and FAISS index from Azure Blob Storage...")
        # Local imports to avoid heavy imports at module import time
        import faiss
        from sentence_transformers import SentenceTransformer
        import gc

        # Load embedding model with memory optimization
        print("🧠 Loading ultra-lightweight embedding model...")
        embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2', device='cpu')  # Much smaller model
        # Force garbage collection after model loading
        gc.collect()
        print("✅ FREE embedding model loaded")

        # Create temporary files for downloaded data
        temp_dir = tempfile.gettempdir()
        FAISS_INDEX_PATH = os.path.join(temp_dir, "ultra_reduced_electrical_grid_index.faiss")
        METADATA_PATH = os.path.join(temp_dir, "ultra_reduced_electrical_grid_metadata.json")

        # Download files from Azure Blob Storage if not already cached
        if not os.path.exists(FAISS_INDEX_PATH):
            print("📥 Downloading FAISS index from Azure Blob Storage...")
            success = await download_file_from_url(FAISS_INDEX_URL, FAISS_INDEX_PATH)
            if not success:
                raise Exception("Failed to download FAISS index from blob storage")
            # Force garbage collection after download
            gc.collect()
        else:
            print("✅ Using cached FAISS index")

        if not os.path.exists(METADATA_PATH):
            print("📥 Downloading metadata from Azure Blob Storage...")
            success = await download_file_from_url(METADATA_URL, METADATA_PATH)
            if not success:
                raise Exception("Failed to download metadata from blob storage")
            # Force garbage collection after download
            gc.collect()
        else:
            print("✅ Using cached metadata")

        # Load FAISS index and metadata
        print("📚 Loading FAISS index and metadata...")
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            texts = json.load(f)

        RAG_AVAILABLE = True
        print(f"✅ RAG system loaded: {len(texts):,} electrical transmission lines indexed (20% ultra-optimized dataset)")
        print(f"📊 FAISS index contains {index.ntotal:,} vectors")
        print("🗂️  Files loaded from Azure Blob Storage and cached locally")

    except Exception as e:
        RAG_AVAILABLE = False
        index = None
        texts = []
        print(f"❌ RAG system not available after lazy load: {e}")
        print("Please ensure Azure Blob Storage URLs are accessible:")
        print(f"- {FAISS_INDEX_URL}")
        print(f"- {METADATA_URL}")

async def generate_ai_answer(query):
    """Generate answer using Gemini AI with RAG (if available)"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Try to retrieve relevant documents
        retrieved_docs = await retrieve_documents(query)
        
        if retrieved_docs and RAG_AVAILABLE:
            # RAG mode: Use retrieved documents as context
            context = "\n\n".join(retrieved_docs)
            prompt = f"""Based on the following context about electrical transmission lines, answer the question accurately and helpfully:

Context:
{context}

Question: {query}

Please provide a clear, informative answer based on the context provided. If the context doesn't contain relevant information, use your general knowledge about electrical grids."""
        else:
            # Fallback mode: General AI response
            prompt = f"""You are a helpful assistant for electrical grid information. 
            Answer the following question about electrical grids, power systems, or related topics:
            
            Question: {query}
            
            If the question is not related to electrical grids or power systems, politely redirect to grid-related topics."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

async def retrieve_documents(query, k=5):
    """Retrieve relevant documents using FAISS similarity search with FREE embeddings"""
    import gc
    # Ensure heavy resources are loaded on first use
    await ensure_rag_loaded()
    if not RAG_AVAILABLE:
        return []
    
    try:
        print(f"🔍 Searching for: {query}")
        
        # Get query embedding using same FREE model as data
        query_embedding = embedding_model.encode([query])
        query_vec = query_embedding.astype("float32")
        
        print(f"📊 Query vector shape: {query_vec.shape}")
        print(f"📊 Index total vectors: {index.ntotal}")
        
        # Search FAISS index
        distances, indices = index.search(query_vec, k)
        
        # Get relevant documents
        relevant_docs = []
        for i, idx in enumerate(indices[0]):
            if idx < len(texts):
                doc = texts[idx]
                distance = distances[0][i]
                print(f"  📄 Found: {doc['id']} (distance: {distance:.3f})")
                relevant_docs.append(doc['content'])
        
        print(f"✅ Retrieved {len(relevant_docs)} relevant documents")
        
        # Clean up memory after search
        del query_embedding, query_vec, distances, indices
        gc.collect()
        
        return relevant_docs
        
    except Exception as e:
        print(f"❌ Error in document retrieval: {e}")
        return []

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/")
async def chat(request: Request, query: str = Form(...)):
    async with request_semaphore:  # Limit concurrent requests
        print(f"📝 Received query: {query}")
        try:
            answer = await generate_ai_answer(query)
            print(f"✅ Generated answer: {len(answer)} characters")
            # Force cleanup after each request
            gc.collect()
            return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": query})
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(f"❌ Error: {error_msg}")
            gc.collect()
            return templates.TemplateResponse("index.html", {"request": request, "answer": error_msg, "query": query})

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "rag_available": RAG_AVAILABLE,
        "documents_indexed": len(texts) if RAG_AVAILABLE else 0,
        "dataset_type": "ultra_reduced_dataset",
        "transmission_lines": len(texts) if RAG_AVAILABLE else 0
    }

@app.get("/warmup")
async def warmup():
    """Endpoint to pre-load the RAG system - call this to download blob storage files"""
    try:
        await ensure_rag_loaded()
        return {
            "status": "warmed_up",
            "rag_available": RAG_AVAILABLE,
            "documents_indexed": len(texts) if RAG_AVAILABLE else 0,
            "message": "RAG system loaded and ready"
        }
    except Exception as e:
        return {
            "status": "warmup_failed",
            "error": str(e),
            "message": "Failed to load RAG system"
        }

@app.get("/info")
async def info():
    """Endpoint to show dataset information"""
    if RAG_AVAILABLE:
        return {
            "title": "Clarity Grid Chatbot - Ultra-Reduced Dataset",
            "description": "Ultra-optimized US electrical transmission lines dataset (20% of original) for low-memory deployment",
            "dataset_size": len(texts),
            "dataset_type": "Ultra-optimized US electrical transmission infrastructure (highest-priority lines)",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2 (FREE)",
            "ai_model": "Google Gemini 2.5 Flash Lite",
            "optimization": "Top 20% prioritized by voltage level, length, operational status, and infrastructure importance",
            "memory_usage": "Ultra-low memory footprint for cloud deployment",
            "features": [
                "16,737 highest-priority transmission lines",
                "Optimized for Render free tier and similar low-memory hosts",
                "Vector similarity search with FAISS",
                "Zero ongoing API costs for embeddings",
                "Real-time query processing",
                "Lazy-loading for minimal startup memory"
            ]
        }
    else:
        return {
            "status": "error",
            "message": "RAG system not available - please check dataset files"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)