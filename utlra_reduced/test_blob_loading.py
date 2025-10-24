#!/usr/bin/env python3
"""
Test script to verify Azure Blob Storage loading works correctly
"""
import asyncio
import tempfile
import os
from app_ultra import download_file_from_url, FAISS_INDEX_URL, METADATA_URL

async def test_blob_loading():
    """Test downloading files from blob storage"""
    print("🧪 Testing Azure Blob Storage file loading...")
    
    # Create temporary files
    temp_dir = tempfile.gettempdir()
    faiss_path = os.path.join(temp_dir, "test_faiss_index.faiss")
    metadata_path = os.path.join(temp_dir, "test_metadata.json")
    
    try:
        # Test FAISS index download
        print(f"📥 Testing FAISS index download from: {FAISS_INDEX_URL}")
        success1 = await download_file_from_url(FAISS_INDEX_URL, faiss_path)
        
        # Test metadata download
        print(f"📥 Testing metadata download from: {METADATA_URL}")
        success2 = await download_file_from_url(METADATA_URL, metadata_path)
        
        if success1 and success2:
            # Check file sizes
            faiss_size = os.path.getsize(faiss_path) / (1024 * 1024)  # MB
            metadata_size = os.path.getsize(metadata_path) / (1024 * 1024)  # MB
            
            print(f"✅ FAISS index downloaded: {faiss_size:.2f} MB")
            print(f"✅ Metadata downloaded: {metadata_size:.2f} MB")
            print(f"📁 Total downloaded: {faiss_size + metadata_size:.2f} MB")
            
            # Test loading with faiss
            try:
                import faiss
                import json
                
                print("🧪 Testing FAISS index loading...")
                index = faiss.read_index(faiss_path)
                print(f"✅ FAISS index loaded: {index.ntotal:,} vectors")
                
                print("🧪 Testing metadata loading...")
                with open(metadata_path, "r", encoding="utf-8") as f:
                    texts = json.load(f)
                print(f"✅ Metadata loaded: {len(texts):,} records")
                
                print("🎉 All tests passed! Blob storage loading works correctly.")
                
            except Exception as e:
                print(f"❌ Error loading files: {e}")
            
            # Cleanup
            try:
                os.remove(faiss_path)
                os.remove(metadata_path)
                print("🧹 Cleaned up temporary files")
            except:
                pass
                
        else:
            print("❌ Failed to download files from blob storage")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_blob_loading())