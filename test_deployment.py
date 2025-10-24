 #!/usr/bin/env python3
"""
Test script for the reduced transmission lines RAG deployment
"""
import requests
import json
import time

def test_deployment(base_url="http://localhost:8002"):
    """Test the deployed application"""
    print("🧪 Testing Reduced Transmission Lines RAG Deployment...")
    
    try:
        # Test 1: Health check (GET /)
        print("\n1️⃣ Testing web interface...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Web interface accessible")
        else:
            print(f"❌ Web interface error: {response.status_code}")
            return False
        
        # Test 2: API query (using form data)
        print("\n2️⃣ Testing API query...")
        test_query = {"query": "Show me high voltage transmission lines"}
        response = requests.post(base_url, 
                               data=test_query,  # Use form data instead of JSON
                               timeout=30)
        
        if response.status_code == 200:
            # Response is HTML, not JSON
            print("✅ API query successful")
            print(f"📊 Response length: {len(response.text)} characters")
            if "transmission" in response.text.lower():
                print("📋 Response contains transmission line information")
        else:
            print(f"❌ API query failed: {response.status_code}")
            return False
        
        # Test 3: Performance check
        print("\n3️⃣ Testing query performance...")
        start_time = time.time()
        response = requests.post(base_url, 
                               data={"query": "Find transmission lines in California"},  # Use form data
                               timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = end_time - start_time
            print(f"✅ Query completed in {response_time:.2f} seconds")
            if response_time < 5.0:
                print("🚀 Excellent performance!")
            elif response_time < 10.0:
                print("✅ Good performance")
            else:
                print("⚠️ Performance could be improved")
        
        print("\n🎉 All tests passed! Deployment is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application. Make sure it's running.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Application may be overloaded.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    # Allow custom URL as command line argument
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    
    print(f"Testing deployment at: {url}")
    success = test_deployment(url)
    
    if success:
        print("\n✅ Deployment test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment test failed!")
        sys.exit(1)