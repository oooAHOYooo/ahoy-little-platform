#!/usr/bin/env python3
"""
Quick test script to verify freemium limits are working
"""
import requests
import json

BASE_URL = "http://localhost:5001"  # Adjust port as needed

def test_collection_limits():
    """Test that collection creation is limited to 3 for free users"""
    print("🧪 Testing Collection Limits...")
    
    # Create 3 collections (should work)
    for i in range(1, 4):
        payload = {
            "name": f"Test Collection {i}",
            "description": f"Test collection number {i}",
            "type": "mixed"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/collections/",
            json=payload,
            # You'll need to add session/auth headers here
        )
        
        if response.status_code == 201:
            print(f"✅ Collection {i} created successfully")
        else:
            print(f"❌ Collection {i} failed: {response.status_code}")
    
    # Try to create 4th collection (should hit paywall)
    payload = {
        "name": "Test Collection 4 - Should Fail",
        "description": "This should trigger the paywall",
        "type": "mixed"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/collections/",
        json=payload,
    )
    
    if response.status_code == 402:
        data = response.json()
        print(f"✅ Paywall triggered correctly: {data.get('message')}")
    else:
        print(f"❌ Expected 402 paywall, got {response.status_code}")

if __name__ == "__main__":
    print("🚀 Freemium Feature Test")
    print("Make sure the server is running first!")
    print("=" * 50)
    
    try:
        test_collection_limits()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on the expected port!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print("\n🎯 Manual Test Steps:")
    print("1. Start the server: python app.py")
    print("2. Go to /my-saves → Collections tab")
    print("3. Create 3 collections")
    print("4. Try to create a 4th → should see paywall modal")
    print("5. Create playlists from collections (3 max)")
    print("6. Check data/user_activity.json for streak tracking")
