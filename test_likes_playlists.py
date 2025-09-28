#!/usr/bin/env python3
"""
Test script for likes/bookmarks and playlists functionality
"""
import requests
import json
import os

BASE_URL = "http://localhost:5000"

def test_activity_endpoints():
    """Test the activity endpoints"""
    print("Testing activity endpoints...")
    
    # Test like endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/activity/like", 
                               json={"id": "test_track_1", "kind": "track"})
        print(f"Like test: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Like test failed: {e}")
    
    # Test bookmark endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/activity/bookmark", 
                               json={"id": "test_track_1", "kind": "track"})
        print(f"Bookmark test: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Bookmark test failed: {e}")

def test_playlist_endpoints():
    """Test the playlist endpoints"""
    print("Testing playlist endpoints...")
    
    # Test create playlist
    try:
        response = requests.post(f"{BASE_URL}/api/playlists", 
                               json={"name": "Test Playlist", "description": "A test playlist"})
        print(f"Create playlist test: {response.status_code} - {response.json()}")
        
        if response.status_code == 200:
            playlist_id = response.json().get("id")
            if playlist_id:
                # Test add item to playlist
                add_response = requests.post(f"{BASE_URL}/api/playlists/{playlist_id}/items", 
                                           json={"id": "test_track_1", "kind": "track"})
                print(f"Add to playlist test: {add_response.status_code} - {add_response.json()}")
                
                # Test list playlists
                list_response = requests.get(f"{BASE_URL}/api/playlists")
                print(f"List playlists test: {list_response.status_code} - {list_response.json()}")
    except Exception as e:
        print(f"Playlist test failed: {e}")

def check_data_files():
    """Check if data files are created"""
    print("Checking data files...")
    
    files_to_check = [
        "data/user_activity.json",
        "data/playlists.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    print(f"   Content: {json.dumps(data, indent=2)[:200]}...")
            except Exception as e:
                print(f"   Error reading: {e}")
        else:
            print(f"❌ {file_path} does not exist")

if __name__ == "__main__":
    print("Testing Ahoy Indie Media - Likes/Bookmarks and Playlists")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        print("Please start the server with: python app.py")
        exit(1)
    
    print()
    test_activity_endpoints()
    print()
    test_playlist_endpoints()
    print()
    check_data_files()
    
    print("\n" + "=" * 60)
    print("Test completed!")
