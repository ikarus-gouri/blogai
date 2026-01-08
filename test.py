import requests

HF_SPACE_URL = "https://gouriikarus3d-blogai.hf.space"  # Changed from blogaiapi

def test_endpoint(method, url, json_data=None):
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(url, json=json_data, timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            print(f"[ERROR] 404 Not Found")
            print(f"Response: {response.text[:300]}")
        elif response.status_code == 200:
            print(f"[SUCCESS] Response: {response.json()}")
        else:
            print(f"Response: {response.text[:300]}")
            
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Connection Error - Space might not be running")
    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout - Space is slow or not responding")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    print()

print(f"Testing Space: {HF_SPACE_URL}\n")
print("="*60)

print("1. Testing Health...")
test_endpoint("GET", f"{HF_SPACE_URL}/")

print("2. Testing Categories...")
test_endpoint("GET", f"{HF_SPACE_URL}/api/categories")

print("3. Testing Analyze Blog...")
test_endpoint("POST", f"{HF_SPACE_URL}/api/blog", {
    "title": "AI in Healthcare",
    "content": "Artificial intelligence is transforming healthcare with machine learning algorithms."
})

print("4. Testing Extract Keywords...")
test_endpoint("POST", f"{HF_SPACE_URL}/api/extract-keywords", {
    "text": "Machine learning and AI are revolutionizing technology",
    "category": "Technology"
})