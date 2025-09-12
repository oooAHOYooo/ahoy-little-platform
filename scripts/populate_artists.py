#!/usr/bin/env python3
"""
Populate artists data from existing shows and music JSON files
"""

import json
import os
from collections import defaultdict
from datetime import datetime

def load_json_file(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def save_json_file(filepath, data):
    """Save JSON data to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {filepath}")
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def create_artist_slug(name):
    """Create URL-friendly slug from artist name"""
    return name.lower().replace(' ', '-').replace('&', 'and').replace("'", '').replace('"', '')

def get_artist_image(artist_name, existing_artists=None):
    """Get appropriate image for artist"""
    if existing_artists and artist_name in existing_artists:
        return existing_artists[artist_name].get('image', '')
    
    # Try to find image from music tracks
    music_data = load_json_file('static/data/music.json')
    if music_data and 'tracks' in music_data:
        for track in music_data['tracks']:
            if track.get('artist') == artist_name and track.get('cover_art'):
                return track['cover_art']
    
    # Try to find image from shows
    shows_data = load_json_file('static/data/shows.json')
    if shows_data and 'shows' in shows_data:
        for show in shows_data['shows']:
            if show.get('host') == artist_name and show.get('thumbnail'):
                return show['thumbnail']
    
    # Default image
    return '/static/img/default-avatar.png'

def populate_artists():
    """Main function to populate artists data"""
    print("🎵 Starting artist population...")
    
    # Load existing data
    music_data = load_json_file('static/data/music.json')
    shows_data = load_json_file('static/data/shows.json')
    existing_artists_data = load_json_file('static/data/artists.json')
    
    if not music_data or not shows_data:
        print("❌ Could not load music or shows data")
        return False
    
    # Create artists dictionary
    artists = {}
    
    # Process existing artists if any
    if existing_artists_data and 'artists' in existing_artists_data:
        for artist in existing_artists_data['artists']:
            artists[artist['name']] = artist
    
    # Process music tracks
    if 'tracks' in music_data:
        print(f"📀 Processing {len(music_data['tracks'])} music tracks...")
        for track in music_data['tracks']:
            artist_name = track.get('artist')
            if not artist_name:
                continue
                
            if artist_name not in artists:
                artists[artist_name] = {
                    'id': f"artist_{len(artists) + 1}",
                    'name': artist_name,
                    'slug': create_artist_slug(artist_name),
                    'type': 'musician',
                    'description': f"Musician and artist: {artist_name}",
                    'image': get_artist_image(artist_name, artists),
                    'social_links': {},
                    'genres': [],
                    'albums': [],
                    'shows': [],
                    'tracks': [],
                    'followers': 0,
                    'verified': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            
            # Add track to artist
            track_info = {
                'id': track['id'],
                'title': track['title'],
                'album': track.get('album', 'Single'),
                'duration': track.get('duration_seconds', 0),
                'genre': track.get('genre', 'Unknown'),
                'added_date': track.get('added_date', datetime.now().isoformat())
            }
            if 'tracks' not in artists[artist_name]:
                artists[artist_name]['tracks'] = []
            artists[artist_name]['tracks'].append(track_info)
            
            # Add genre if not already present
            genre = track.get('genre', 'Unknown')
            if 'genres' not in artists[artist_name]:
                artists[artist_name]['genres'] = []
            if genre not in artists[artist_name]['genres']:
                artists[artist_name]['genres'].append(genre)
    
    # Process shows
    if 'shows' in shows_data:
        print(f"🎬 Processing {len(shows_data['shows'])} shows...")
        for show in shows_data['shows']:
            host_name = show.get('host')
            if not host_name:
                continue
                
            if host_name not in artists:
                artists[host_name] = {
                    'id': f"artist_{len(artists) + 1}",
                    'name': host_name,
                    'slug': create_artist_slug(host_name),
                    'type': 'host',
                    'description': f"Show host and content creator: {host_name}",
                    'image': get_artist_image(host_name, artists),
                    'social_links': {},
                    'genres': [],
                    'albums': [],
                    'shows': [],
                    'tracks': [],
                    'followers': 0,
                    'verified': False,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            
            # Add show to artist
            show_info = {
                'id': show['id'],
                'title': show['title'],
                'type': show.get('type', 'episode'),
                'duration': show.get('duration_seconds', 0),
                'category': show.get('category', 'Unknown'),
                'published_date': show.get('published_date', datetime.now().isoformat())
            }
            if 'shows' not in artists[host_name]:
                artists[host_name]['shows'] = []
            artists[host_name]['shows'].append(show_info)
            
            # Add category as genre if not already present
            category = show.get('category', 'Unknown')
            if 'genres' not in artists[host_name]:
                artists[host_name]['genres'] = []
            if category not in artists[host_name]['genres']:
                artists[host_name]['genres'].append(category)
    
    # Convert to list and sort
    artists_list = list(artists.values())
    artists_list.sort(key=lambda x: x['name'])
    
    # Create final data structure
    artists_data = {
        'artists': artists_list,
        'total_count': len(artists_list),
        'last_updated': datetime.now().isoformat()
    }
    
    # Save to file
    success = save_json_file('static/data/artists.json', artists_data)
    
    if success:
        print(f"✅ Successfully populated {len(artists_list)} artists")
        print(f"📊 Stats:")
        print(f"   - Musicians: {len([a for a in artists_list if a.get('type') == 'musician'])}")
        print(f"   - Hosts: {len([a for a in artists_list if a.get('type') == 'host'])}")
        print(f"   - Total tracks: {sum(len(a.get('tracks', [])) for a in artists_list)}")
        print(f"   - Total shows: {sum(len(a.get('shows', [])) for a in artists_list)}")
        return True
    else:
        print("❌ Failed to save artists data")
        return False

if __name__ == "__main__":
    populate_artists()
