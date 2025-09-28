#!/usr/bin/env python3
"""
Robust User Management System for Ahoy Indie Media
Handles user registration, authentication, and data management
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

class UserManager:
    def __init__(self, users_file: str = 'data/users.json'):
        self.users_file = users_file
        self.ensure_data_directory()
        self.users = self.load_users()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
    
    def load_users(self) -> Dict:
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "ahoy_indie_media_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str, display_name: str = None) -> Dict[str, Any]:
        """Create a new user"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        user_data = {
            'user_id': user_id,
            'username': username,
            'password': self.hash_password(password),
            'email': email,
            'display_name': display_name or username,
            'created_at': now,
            'last_login': now,
            'profile': {
                'username': username,
                'display_name': display_name or username,
                'email': email,
                'avatar_url': '/static/img/default-avatar.png',
                'bio': '',
                'location': '',
                'website': '',
                'created_at': now,
                'preferences': {
                    'theme': 'default',
                    'autoplay': True,
                    'notifications': True,
                    'privacy': 'public'
                }
            },
            'saves': {
                'saved_tracks': [],
                'saved_shows': [],
                'saved_artists': [],
                'liked_content': [],
                'recently_played': [],
                'playlists': [],
                'collections': [],
                'boards': []
            },
            'activity': {
                'total_plays': 0,
                'total_saves': 0,
                'total_playlists': 0,
                'last_active': now
            },
            'subscription': {
                'type': 'free',
                'expires_at': None,
                'features': ['basic_saves', 'basic_playlists']
            }
        }
        
        self.users[username] = user_data
        self.save_users()
        return user_data
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user login"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        if user['password'] != self.hash_password(password):
            return None
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        user['activity']['last_active'] = datetime.now().isoformat()
        self.save_users()
        
        return user
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return self.users.get(username)
    
    def update_user_profile(self, username: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        user['profile'].update(profile_data)
        user['display_name'] = profile_data.get('display_name', user['display_name'])
        self.save_users()
        return True
    
    def save_content(self, username: str, content_type: str, content_id: str, content_data: Dict[str, Any] = None) -> bool:
        """Save content to user's saves"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        save_key = f"saved_{content_type}s"
        
        if save_key not in user['saves']:
            user['saves'][save_key] = []
        
        # Check if already saved
        existing_save = next((s for s in user['saves'][save_key] if s['id'] == content_id), None)
        if existing_save:
            return True  # Already saved
        
        save_item = {
            'id': content_id,
            'type': content_type,
            'saved_at': datetime.now().isoformat(),
            'data': content_data or {}
        }
        
        user['saves'][save_key].append(save_item)
        user['activity']['total_saves'] += 1
        self.save_users()
        return True
    
    def unsave_content(self, username: str, content_type: str, content_id: str) -> bool:
        """Remove content from user's saves"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        save_key = f"saved_{content_type}s"
        
        if save_key not in user['saves']:
            return False
        
        # Remove the save
        user['saves'][save_key] = [s for s in user['saves'][save_key] if s['id'] != content_id]
        user['activity']['total_saves'] = max(0, user['activity']['total_saves'] - 1)
        self.save_users()
        return True
    
    def is_content_saved(self, username: str, content_type: str, content_id: str) -> bool:
        """Check if content is saved by user"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        save_key = f"saved_{content_type}s"
        
        if save_key not in user['saves']:
            return False
        
        return any(s['id'] == content_id for s in user['saves'][save_key])
    
    def get_saved_content(self, username: str, content_type: str) -> List[Dict[str, Any]]:
        """Get user's saved content of specific type"""
        if username not in self.users:
            return []
        
        user = self.users[username]
        save_key = f"saved_{content_type}s"
        return user['saves'].get(save_key, [])
    
    def create_playlist(self, username: str, name: str, description: str = "", is_public: bool = False) -> Optional[str]:
        """Create a new playlist"""
        if username not in self.users:
            return None
        
        playlist_id = str(uuid.uuid4())
        playlist = {
            'id': playlist_id,
            'name': name,
            'description': description,
            'is_public': is_public,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tracks': [],
            'shows': [],
            'artists': [],
            'total_items': 0,
            'total_duration': 0,
            'tags': [],
            'cover_art': None
        }
        
        user = self.users[username]
        user['saves']['playlists'].append(playlist)
        user['activity']['total_playlists'] += 1
        self.save_users()
        return playlist_id
    
    def add_to_playlist(self, username: str, playlist_id: str, content_type: str, content_id: str, content_data: Dict[str, Any] = None) -> bool:
        """Add content to playlist"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        playlist = next((p for p in user['saves']['playlists'] if p['id'] == playlist_id), None)
        
        if not playlist:
            return False
        
        # Check if already in playlist
        content_list = playlist.get(content_type + 's', [])
        if any(item['id'] == content_id for item in content_list):
            return True  # Already in playlist
        
        item = {
            'id': content_id,
            'added_at': datetime.now().isoformat(),
            'data': content_data or {}
        }
        
        playlist[content_type + 's'].append(item)
        playlist['total_items'] = sum(len(playlist.get(key, [])) for key in ['tracks', 'shows', 'artists'])
        playlist['updated_at'] = datetime.now().isoformat()
        
        self.save_users()
        return True
    
    def remove_from_playlist(self, username: str, playlist_id: str, content_type: str, content_id: str) -> bool:
        """Remove content from playlist"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        playlist = next((p for p in user['saves']['playlists'] if p['id'] == playlist_id), None)
        
        if not playlist:
            return False
        
        content_list = playlist.get(content_type + 's', [])
        playlist[content_type + 's'] = [item for item in content_list if item['id'] != content_id]
        playlist['total_items'] = sum(len(playlist.get(key, [])) for key in ['tracks', 'shows', 'artists'])
        playlist['updated_at'] = datetime.now().isoformat()
        
        self.save_users()
        return True
    
    def get_playlist(self, username: str, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Get specific playlist"""
        if username not in self.users:
            return None
        
        user = self.users[username]
        return next((p for p in user['saves']['playlists'] if p['id'] == playlist_id), None)
    
    def get_user_playlists(self, username: str) -> List[Dict[str, Any]]:
        """Get all user playlists"""
        if username not in self.users:
            return []
        
        user = self.users[username]
        return user['saves'].get('playlists', [])
    
    def delete_playlist(self, username: str, playlist_id: str) -> bool:
        """Delete playlist"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        user['saves']['playlists'] = [p for p in user['saves']['playlists'] if p['id'] != playlist_id]
        user['activity']['total_playlists'] = max(0, user['activity']['total_playlists'] - 1)
        self.save_users()
        return True
    
    def like_content(self, username: str, content_type: str, content_id: str, content_data: Dict[str, Any] = None) -> bool:
        """Like content"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        
        # Check if already liked
        existing_like = next((l for l in user['saves']['liked_content'] if l['id'] == content_id and l['type'] == content_type), None)
        if existing_like:
            return True  # Already liked
        
        like_item = {
            'id': content_id,
            'type': content_type,
            'liked_at': datetime.now().isoformat(),
            'data': content_data or {}
        }
        
        user['saves']['liked_content'].append(like_item)
        self.save_users()
        return True
    
    def unlike_content(self, username: str, content_type: str, content_id: str) -> bool:
        """Unlike content"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        user['saves']['liked_content'] = [
            l for l in user['saves']['liked_content'] 
            if not (l['id'] == content_id and l['type'] == content_type)
        ]
        self.save_users()
        return True
    
    def is_content_liked(self, username: str, content_type: str, content_id: str) -> bool:
        """Check if content is liked"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        return any(l['id'] == content_id and l['type'] == content_type for l in user['saves']['liked_content'])
    
    def add_recently_played(self, username: str, content_type: str, content_id: str, content_data: Dict[str, Any] = None) -> bool:
        """Add to recently played"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        
        # Remove if already exists
        user['saves']['recently_played'] = [
            r for r in user['saves']['recently_played'] 
            if not (r['id'] == content_id and r['type'] == content_type)
        ]
        
        # Add to beginning
        recent_item = {
            'id': content_id,
            'type': content_type,
            'played_at': datetime.now().isoformat(),
            'data': content_data or {}
        }
        
        user['saves']['recently_played'].insert(0, recent_item)
        
        # Keep only last 100 items
        user['saves']['recently_played'] = user['saves']['recently_played'][:100]
        user['activity']['total_plays'] += 1
        user['activity']['last_active'] = datetime.now().isoformat()
        
        self.save_users()
        return True
    
    def create_playlist(self, username: str, name: str, description: str = "", color: str = "#6366f1", is_public: bool = False) -> Optional[str]:
        """Create a new playlist"""
        if username not in self.users:
            return None
        
        playlist_id = str(uuid.uuid4())
        playlist = {
            'id': playlist_id,
            'name': name,
            'description': description,
            'color': color,
            'is_public': is_public,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'tracks': [],
            'shows': [],
            'artists': [],
            'total_items': 0,
            'cover_art': None,
            'tags': []
        }
        
        user = self.users[username]
        user['saves']['playlists'].append(playlist)
        user['activity']['total_playlists'] += 1
        self.save_users()
        return playlist_id
    
    def add_to_playlist(self, username: str, playlist_id: str, content_type: str, content_id: str, content_data: Dict[str, Any] = None) -> bool:
        """Add content to playlist"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        playlist = next((p for p in user['saves']['playlists'] if p['id'] == playlist_id), None)
        
        if not playlist:
            return False
        
        # Check if already in playlist
        content_list = playlist.get(content_type + 's', [])
        if any(item['id'] == content_id for item in content_list):
            return True  # Already in playlist
        
        item = {
            'id': content_id,
            'added_at': datetime.now().isoformat(),
            'data': content_data or {}
        }
        
        playlist[content_type + 's'].append(item)
        playlist['total_items'] = sum(len(playlist.get(key, [])) for key in ['tracks', 'shows', 'artists'])
        playlist['updated_at'] = datetime.now().isoformat()
        
        self.save_users()
        return True
    
    def remove_from_playlist(self, username: str, playlist_id: str, content_type: str, content_id: str) -> bool:
        """Remove content from playlist"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        playlist = next((p for p in user['saves']['playlists'] if p['id'] == playlist_id), None)
        
        if not playlist:
            return False
        
        content_list = playlist.get(content_type + 's', [])
        playlist[content_type + 's'] = [item for item in content_list if item['id'] != content_id]
        playlist['total_items'] = sum(len(playlist.get(key, [])) for key in ['tracks', 'shows', 'artists'])
        playlist['updated_at'] = datetime.now().isoformat()
        
        self.save_users()
        return True
    
    
    def get_user_stats(self, username: str) -> Dict[str, Any]:
        """Get user statistics"""
        if username not in self.users:
            return {}
        
        user = self.users[username]
        return {
            'total_saves': user['activity']['total_saves'],
            'total_playlists': user['activity']['total_playlists'],
            'total_plays': user['activity']['total_plays'],
            'saved_tracks': len(user['saves'].get('saved_tracks', [])),
            'saved_shows': len(user['saves'].get('saved_shows', [])),
            'saved_artists': len(user['saves'].get('saved_artists', [])),
            'liked_content': len(user['saves'].get('liked_content', [])),
            'recently_played': len(user['saves'].get('recently_played', [])),
            'playlists': len(user['saves'].get('playlists', [])),
        }

# Global user manager instance
user_manager = UserManager()
