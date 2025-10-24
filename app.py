from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import numpy as np
import faiss
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Clarity Grid Chatbot - Reduced Dataset (41,843 Lines)")
templates = Jinja2Templates(directory="templates")

# Configure Gemini AI
api_key = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")
genai.configure(api_key=api_key)

# Local file paths for reduced dataset (41,843 records)
FAISS_INDEX_PATH = "reduced_electrical_grid_index.faiss"
METADATA_PATH = "reduced_electrical_grid_metadata.json"

# Load FREE sentence transformer model for query embeddings
print("📥 Loading FREE embedding model for queries...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ FREE embedding model loaded")

# Load FAISS index and metadata from local files
try:
    print("📂 Loading REDUCED dataset from local files...")
    
    # Check if files exist
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(f"FAISS index file not found: {FAISS_INDEX_PATH}")
    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")
    
    # Load FAISS index
    index = faiss.read_index(FAISS_INDEX_PATH)
    
    # Load metadata
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        texts = json.load(f)
    
    RAG_AVAILABLE = True
    print(f"✅ RAG system loaded: {len(texts):,} electrical transmission lines indexed (50% optimized dataset)")
    print(f"📊 FAISS index contains {index.ntotal:,} vectors")
    
except Exception as e:
    RAG_AVAILABLE = False
    index = None
    texts = []
    print(f"❌ RAG system not available: {e}")
    print("Please ensure the following files are in this directory:")
    print("- reduced_electrical_grid_index.faiss")
    print("- reduced_electrical_grid_metadata.json")

def generate_ai_answer(query):
    """Generate answer using Gemini AI with RAG (if available)"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Try to retrieve relevant documents
        retrieved_docs = retrieve_documents(query)
        
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

def retrieve_documents(query, k=5):
    """Retrieve relevant documents using FAISS similarity search with FREE embeddings"""
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
        return relevant_docs
        
    except Exception as e:
        print(f"❌ Error in document retrieval: {e}")
        return []

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/")
async def chat(request: Request, query: str = Form(...)):
    print(f"📝 Received query: {query}")
    try:
        answer = generate_ai_answer(query)
        print(f"✅ Generated answer: {len(answer)} characters")
        return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": query})
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return templates.TemplateResponse("index.html", {"request": request, "answer": error_msg, "query": query})

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "rag_available": RAG_AVAILABLE,
        "documents_indexed": len(texts) if RAG_AVAILABLE else 0,
        "dataset_type": "reduced_dataset",
        "transmission_lines": len(texts) if RAG_AVAILABLE else 0
    }

@app.get("/info")
async def info():
    """Endpoint to show dataset information"""
    if RAG_AVAILABLE:
        return {
            "title": "Clarity Grid Chatbot - Reduced Dataset",
            "description": "Optimized US electrical transmission lines dataset (50% of full) with RAG-powered search",
            "dataset_size": len(texts),
            "dataset_type": "Optimized US electrical transmission infrastructure (high-priority lines)",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2 (FREE)",
            "ai_model": "Google Gemini 2.5 Flash Lite",
            "optimization": "Prioritized by voltage level, length, and operational status",
            "features": [
                "41,843 high-priority transmission lines",
                "Optimized for deployment on resource-constrained platforms",
                "Vector similarity search with FAISS",
                "Zero ongoing API costs for embeddings",
                "Real-time query processing"
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