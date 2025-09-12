#!/usr/bin/env python3
"""
Sample Data Generator for Ahoy Indie Media
Creates sample JSON data files for development and testing
"""

import json
import os
from datetime import datetime, timedelta
import random

def create_sample_music():
    """Create sample music data"""
    tracks = [
        {
            "id": "track_001",
            "title": "Midnight City",
            "artist": "M83",
            "album": "Hurry Up, We're Dreaming",
            "genre": "Electronic",
            "duration_seconds": 245,
            "audio_url": "https://example.com/audio/midnight-city.mp3",
            "preview_url": "https://example.com/preview/midnight-city.mp3",
            "cover_art": "https://example.com/covers/midnight-city.jpg",
            "added_date": "2024-01-15",
            "tags": ["electronic", "dreamy", "atmospheric"],
            "artist_slug": "m83"
        },
        {
            "id": "track_002",
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "album": "A Night at the Opera",
            "genre": "Rock",
            "duration_seconds": 355,
            "audio_url": "https://example.com/audio/bohemian-rhapsody.mp3",
            "preview_url": "https://example.com/preview/bohemian-rhapsody.mp3",
            "cover_art": "https://example.com/covers/bohemian-rhapsody.jpg",
            "added_date": "2024-01-10",
            "tags": ["rock", "classic", "opera"],
            "artist_slug": "queen"
        },
        {
            "id": "track_003",
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "album": "After Hours",
            "genre": "Pop",
            "duration_seconds": 200,
            "audio_url": "https://example.com/audio/blinding-lights.mp3",
            "preview_url": "https://example.com/preview/blinding-lights.mp3",
            "cover_art": "https://example.com/covers/blinding-lights.jpg",
            "added_date": "2024-01-20",
            "tags": ["pop", "synthwave", "retro"],
            "artist_slug": "the-weeknd"
        }
    ]
    
    return {"tracks": tracks}

def create_sample_shows():
    """Create sample shows data"""
    shows = [
        {
            "id": "show_001",
            "title": "The Rob Show - Ep 8 - The Gypsies - Clip 4",
            "host": "Rob Meglio",
            "description": "A deep dive into the world of gypsy music and culture, featuring live performances and interviews with local artists.",
            "duration_seconds": 376,
            "video_url": "https://cdn.jwplayer.com/videos/4f55y55N-GVOzihKP.mp4",
            "trailer_url": "https://cdn.jwplayer.com/videos/4f55y55N-GVOzihKP-preview.mp4",
            "thumbnail": "https://cdn.jwplayer.com/v2/media/4f55y55N/poster.jpg",
            "published_date": "2024-01-20",
            "views": 1250,
            "type": "episode",
            "is_live": False,
            "tags": ["music", "culture", "interview"],
            "host_slug": "rob-meglio"
        },
        {
            "id": "show_002",
            "title": "Indie Spotlight: New Haven Sessions",
            "host": "Sarah Chen",
            "description": "Live acoustic performances from emerging indie artists in the New Haven area, recorded in intimate settings.",
            "duration_seconds": 1800,
            "video_url": "https://example.com/videos/indie-spotlight-new-haven.mp4",
            "trailer_url": "https://example.com/videos/indie-spotlight-new-haven-preview.mp4",
            "thumbnail": "https://example.com/thumbnails/indie-spotlight-new-haven.jpg",
            "published_date": "2024-01-18",
            "views": 890,
            "type": "episode",
            "is_live": False,
            "tags": ["indie", "acoustic", "live"],
            "host_slug": "sarah-chen"
        }
    ]
    
    return {"shows": shows}

def create_sample_artists():
    """Create sample artists data"""
    artists = [
        {
            "id": "artist_001",
            "name": "Rob Meglio",
            "slug": "rob-meglio",
            "genre": "Alternative Rock",
            "bio": "A passionate musician and host who explores the intersection of culture and music through intimate conversations and live performances.",
            "avatar": "https://example.com/avatars/rob-meglio.jpg",
            "cover_image": "https://example.com/covers/rob-meglio-cover.jpg",
            "location": "New Haven, CT",
            "website": "https://robmeglio.com",
            "social_links": {
                "instagram": "https://instagram.com/robmeglio",
                "twitter": "https://twitter.com/robmeglio",
                "youtube": "https://youtube.com/robmeglio"
            },
            "track_count": 15,
            "show_count": 8,
            "followers": 2500,
            "total_plays": 45000,
            "tags": ["alternative", "culture", "host"],
            "verified": True
        },
        {
            "id": "artist_002",
            "name": "Sarah Chen",
            "slug": "sarah-chen",
            "genre": "Indie Folk",
            "bio": "An emerging indie folk artist known for her haunting melodies and introspective lyrics, often performing in intimate acoustic settings.",
            "avatar": "https://example.com/avatars/sarah-chen.jpg",
            "cover_image": "https://example.com/covers/sarah-chen-cover.jpg",
            "location": "New Haven, CT",
            "website": "https://sarahchenmusic.com",
            "social_links": {
                "instagram": "https://instagram.com/sarahchenmusic",
                "spotify": "https://open.spotify.com/artist/sarahchen",
                "bandcamp": "https://sarahchen.bandcamp.com"
            },
            "track_count": 8,
            "show_count": 12,
            "followers": 1200,
            "total_plays": 18000,
            "tags": ["indie", "folk", "acoustic"],
            "verified": False
        }
    ]
    
    return {"artists": artists}

def create_directories():
    """Create necessary directories"""
    directories = [
        'data',
        'static/data',
        'static/css',
        'static/js',
        'static/img',
        'templates',
        'scripts'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def main():
    """Main function to generate sample data"""
    print("Creating Ahoy Indie Media sample data...")
    
    # Create directories
    create_directories()
    
    # Create sample data
    music_data = create_sample_music()
    shows_data = create_sample_shows()
    artists_data = create_sample_artists()
    
    # Write JSON files
    with open('static/data/music.json', 'w') as f:
        json.dump(music_data, f, indent=2)
    print("Created static/data/music.json")
    
    with open('static/data/shows.json', 'w') as f:
        json.dump(shows_data, f, indent=2)
    print("Created static/data/shows.json")
    
    with open('static/data/artists.json', 'w') as f:
        json.dump(artists_data, f, indent=2)
    print("Created static/data/artists.json")
    
    # Create empty user data files
    with open('data/users.json', 'w') as f:
        json.dump({}, f, indent=2)
    print("Created data/users.json")
    
    with open('data/user_activity.json', 'w') as f:
        json.dump({}, f, indent=2)
    print("Created data/user_activity.json")
    
    print("\nSample data generation complete!")
    print("You can now run the Flask application with: python app.py")

if __name__ == "__main__":
    main()
