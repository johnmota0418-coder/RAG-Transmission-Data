#!/usr/bin/env python3
"""
Create an ultra-reduced dataset (20% of original) for minimal memory deployment
"""
import json
import numpy as np
import random

def create_ultra_reduced_dataset(input_metadata="reduced_electrical_grid_metadata.json", 
                                input_index="reduced_electrical_grid_index.faiss",
                                output_metadata="ultra_reduced_electrical_grid_metadata.json",
                                output_index="ultra_reduced_electrical_grid_index.faiss",
                                reduction_factor=0.4):  # 20% of original = 40% of current 50%
    """
    Create ultra-reduced dataset by selecting high-priority transmission lines
    """
    print(f"🔄 Creating ultra-reduced dataset ({reduction_factor*100:.0f}% of current dataset)...")
    
    # Load current metadata
    with open(input_metadata, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    print(f"📊 Current dataset: {len(current_data):,} transmission lines")
    
    # Calculate target size
    target_size = int(len(current_data) * reduction_factor)
    print(f"🎯 Target size: {target_size:,} transmission lines")
    
    # Priority scoring for transmission lines
    def get_priority_score(item):
        score = 0
        content = item.get('content', '').lower()
        
        # High voltage gets highest priority
        if 'kv' in content:
            # Extract voltage values and prioritize higher voltages
            voltage_terms = ['765kv', '500kv', '345kv', '230kv', '138kv', '115kv']
            for i, term in enumerate(voltage_terms):
                if term in content:
                    score += (len(voltage_terms) - i) * 100
                    break
        
        # Operational status priority
        if 'in service' in content or 'operating' in content:
            score += 50
        
        # Length-based priority (longer lines are often more important)
        if 'mile' in content or 'km' in content:
            score += 30
        
        # Interstate/major connections
        if any(term in content for term in ['interstate', 'transmission', 'substation']):
            score += 25
        
        # Major utility companies (indicate important infrastructure)
        major_utilities = ['pge', 'duke', 'southern', 'firstenergy', 'exelon', 'dominion']
        if any(utility in content for utility in major_utilities):
            score += 20
        
        # Add some randomness to avoid clustering
        score += random.randint(0, 10)
        
        return score
    
    # Score and sort all items
    print("🔍 Scoring transmission lines by priority...")
    scored_items = []
    for i, item in enumerate(current_data):
        score = get_priority_score(item)
        scored_items.append((score, i, item))
    
    # Sort by score (highest first) and select top items
    scored_items.sort(key=lambda x: x[0], reverse=True)
    selected_items = [item for _, _, item in scored_items[:target_size]]
    selected_indices = [idx for _, idx, _ in scored_items[:target_size]]
    
    print(f"✅ Selected {len(selected_items):,} highest priority transmission lines")
    
    # Save ultra-reduced metadata
    with open(output_metadata, 'w', encoding='utf-8') as f:
        json.dump(selected_items, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved ultra-reduced metadata: {output_metadata}")
    
    # Load and reduce FAISS index
    try:
        import faiss
        print("📂 Loading current FAISS index...")
        current_index = faiss.read_index(input_index)
        
        print(f"📊 Current index vectors: {current_index.ntotal:,}")
        
        # Extract vectors for selected indices
        print("🔄 Extracting vectors for selected items...")
        selected_vectors = []
        for idx in selected_indices:
            if idx < current_index.ntotal:
                vector = current_index.reconstruct(idx)
                selected_vectors.append(vector)
        
        # Create new FAISS index
        if selected_vectors:
            vectors_array = np.array(selected_vectors, dtype=np.float32)
            print(f"📊 Creating new index with {len(selected_vectors):,} vectors...")
            
            # Create new index with same dimensions
            dimension = vectors_array.shape[1]
            new_index = faiss.IndexFlatIP(dimension)  # Inner product index
            new_index.add(vectors_array)
            
            # Save new index
            faiss.write_index(new_index, output_index)
            print(f"💾 Saved ultra-reduced FAISS index: {output_index}")
            print(f"📊 New index contains {new_index.ntotal:,} vectors")
        else:
            print("❌ No vectors to save")
            
    except ImportError:
        print("⚠️ FAISS not available, skipping index reduction")
    except Exception as e:
        print(f"❌ Error processing FAISS index: {e}")
    
    # Calculate file sizes
    import os
    if os.path.exists(output_metadata):
        metadata_size = os.path.getsize(output_metadata) / (1024*1024)
        print(f"📊 Ultra-reduced metadata size: {metadata_size:.1f} MB")
    
    if os.path.exists(output_index):
        index_size = os.path.getsize(output_index) / (1024*1024)
        print(f"📊 Ultra-reduced index size: {index_size:.1f} MB")
    
    print("\n🎉 Ultra-reduced dataset created successfully!")
    print(f"📈 Reduction: {len(current_data):,} → {len(selected_items):,} lines")
    print(f"📊 Size reduction: ~{(1-reduction_factor)*100:.0f}% smaller")
    
    return len(selected_items)

if __name__ == "__main__":
    random.seed(42)  # For reproducible results
    create_ultra_reduced_dataset()