from flask import Flask, render_template, jsonify, request, session, send_from_directory
import os
import json
from datetime import datetime, timedelta
import random
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'ahoy-indie-media-secret-2025')

# Simple user management (no external dependencies)
USERS_FILE = 'data/users.json'
ACTIVITY_FILE = 'data/user_activity.json'

def load_json_data(filename, default=None):
    """Load JSON data from file with fallback"""
    try:
        with open(f'static/data/{filename}', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default or {}

def load_users():
    """Load user data"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    """Save user data"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def auth_required(f):
    """Simple auth decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    """Main discovery page with Now Playing feed"""
    return render_template('home.html')

@app.route('/music')
def music():
    """Music library page"""
    return render_template('music.html')

@app.route('/shows')
def shows():
    """Shows/video content page"""
    return render_template('shows.html')

@app.route('/artists')
def artists():
    """Artists directory page"""
    return render_template('artists.html')

@app.route('/player')
def player():
    """Full-screen player page"""
    media_id = request.args.get('id')
    media_type = request.args.get('type', 'music')  # music, show, video
    return render_template('player.html', media_id=media_id, media_type=media_type)

@app.route('/artist/<artist_name>')
def artist_profile(artist_name):
    """Individual artist profile page"""
    return render_template('artist_profile.html', artist_name=artist_name)

# API Endpoints
@app.route('/api/now-playing')
def api_now_playing():
    """Get curated now playing feed with 30s previews"""
    music_data = load_json_data('music.json', {'tracks': []})
    shows_data = load_json_data('shows.json', {'shows': []})
    
    # Combine and curate content for discovery feed
    feed_items = []
    
    # Add featured music (with preview clips)
    for track in music_data.get('tracks', [])[:5]:
        if track.get('preview_url'):  # Only include if has preview
            feed_items.append({
                'id': track['id'],
                'type': 'music',
                'title': track['title'],
                'artist': track['artist'],
                'preview_url': track['preview_url'],
                'cover_art': track['cover_art'],
                'duration': 30,  # Preview length
                'full_url': track['audio_url']
            })
    
    # Add featured shows
    for show in shows_data.get('shows', [])[:3]:
        if show.get('trailer_url'):
            feed_items.append({
                'id': show['id'],
                'type': 'show',
                'title': show['title'],
                'artist': show.get('host', 'Ahoy Indie Media'),
                'preview_url': show['trailer_url'],
                'cover_art': show['thumbnail'],
                'duration': 30,
                'full_url': show['video_url']
            })
    
    # Shuffle for discovery
    random.shuffle(feed_items)
    
    return jsonify({'feed': feed_items})

@app.route('/api/music')
def api_music():
    """Get all music data"""
    music_data = load_json_data('music.json', {'tracks': []})
    return jsonify(music_data)

@app.route('/api/shows')
def api_shows():
    """Get all shows/video content"""
    shows_data = load_json_data('shows.json', {'shows': []})
    return jsonify(shows_data)

@app.route('/api/artists')
def api_artists():
    """Get artists directory"""
    artists_data = load_json_data('artists.json', {'artists': []})
    return jsonify(artists_data)

@app.route('/api/artist/<artist_name>')
def api_artist_profile(artist_name):
    """Get specific artist data"""
    artists_data = load_json_data('artists.json', {'artists': []})
    music_data = load_json_data('music.json', {'tracks': []})
    shows_data = load_json_data('shows.json', {'shows': []})
    
    # Find artist
    artist = None
    for a in artists_data.get('artists', []):
        if a.get('slug') == artist_name or a.get('name').lower().replace(' ', '-') == artist_name:
            artist = a
            break
    
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    
    # Get artist's content
    artist_tracks = [t for t in music_data.get('tracks', []) if t.get('artist_slug') == artist_name]
    artist_shows = [s for s in shows_data.get('shows', []) if s.get('host_slug') == artist_name]
    
    return jsonify({
        'artist': artist,
        'tracks': artist_tracks,
        'shows': artist_shows
    })

@app.route('/api/daily-playlist')
def api_daily_playlist():
    """Generate seeded daily playlist"""
    music_data = load_json_data('music.json', {'tracks': []})
    
    # Get today's seed
    today_str = datetime.now().strftime('%Y%m%d')
    seed = int(today_str)
    random.seed(seed)
    
    tracks = music_data.get('tracks', [])
    if not tracks:
        return jsonify({'playlist': [], 'message': 'No tracks available'})
    
    # Create playlist aiming for ~1 hour
    shuffled_tracks = random.sample(tracks, min(len(tracks), 20))
    playlist = []
    total_duration = 0
    
    for track in shuffled_tracks:
        duration = track.get('duration_seconds', 180)
        if total_duration < 3600 or len(playlist) == 0:
            playlist.append(track)
            total_duration += duration
        else:
            break
    
    return jsonify({
        'playlist': playlist,
        'total_duration': total_duration,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'seed': seed
    })

@app.route('/api/search')
def api_search():
    """Universal search"""
    query = request.args.get('q', '').lower()
    
    music_data = load_json_data('music.json', {'tracks': []})
    shows_data = load_json_data('shows.json', {'shows': []})
    artists_data = load_json_data('artists.json', {'artists': []})
    
    results = {
        'tracks': [],
        'shows': [],
        'artists': []
    }
    
    # Search music
    for track in music_data.get('tracks', []):
        if (query in track.get('title', '').lower() or 
            query in track.get('artist', '').lower() or
            query in track.get('tags', '').lower()):
            results['tracks'].append(track)
    
    # Search shows
    for show in shows_data.get('shows', []):
        if (query in show.get('title', '').lower() or
            query in show.get('description', '').lower() or
            query in show.get('host', '').lower()):
            results['shows'].append(show)
    
    # Search artists
    for artist in artists_data.get('artists', []):
        if (query in artist.get('name', '').lower() or
            query in artist.get('bio', '').lower() or
            query in artist.get('genre', '').lower()):
            results['artists'].append(artist)
    
    return jsonify(results)

# User Playlist & Organization Features
@app.route('/api/user/playlists', methods=['GET', 'POST'])
@auth_required
def user_playlists():
    """Get user playlists or create new playlist"""
    username = session.get('username')
    users = load_users()
    
    if 'playlists' not in users[username]:
        users[username]['playlists'] = []
    
    if request.method == 'POST':
        data = request.json
        playlist = {
            'id': hashlib.md5(f"{username}-{datetime.now().isoformat()}".encode()).hexdigest()[:8],
            'name': data.get('name'),
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'items': [],
            'is_public': data.get('is_public', False),
            'tags': data.get('tags', [])
        }
        
        users[username]['playlists'].append(playlist)
        save_users(users)
        return jsonify({'success': True, 'playlist': playlist})
    
    return jsonify(users[username]['playlists'])

@app.route('/api/user/playlists/<playlist_id>', methods=['GET', 'PUT', 'DELETE'])
@auth_required
def manage_playlist(playlist_id):
    """Get, update, or delete specific playlist"""
    username = session.get('username')
    users = load_users()
    
    playlist = None
    playlist_index = None
    
    for i, p in enumerate(users[username].get('playlists', [])):
        if p['id'] == playlist_id:
            playlist = p
            playlist_index = i
            break
    
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    
    if request.method == 'DELETE':
        del users[username]['playlists'][playlist_index]
        save_users(users)
        return jsonify({'success': True})
    
    if request.method == 'PUT':
        data = request.json
        playlist['name'] = data.get('name', playlist['name'])
        playlist['description'] = data.get('description', playlist['description'])
        playlist['is_public'] = data.get('is_public', playlist['is_public'])
        playlist['tags'] = data.get('tags', playlist['tags'])
        playlist['updated_at'] = datetime.now().isoformat()
        
        users[username]['playlists'][playlist_index] = playlist
        save_users(users)
        return jsonify({'success': True, 'playlist': playlist})
    
    return jsonify(playlist)

@app.route('/api/user/playlists/<playlist_id>/items', methods=['POST', 'DELETE'])
@auth_required
def manage_playlist_items(playlist_id):
    """Add or remove items from playlist"""
    username = session.get('username')
    users = load_users()
    
    playlist = None
    playlist_index = None
    
    for i, p in enumerate(users[username].get('playlists', [])):
        if p['id'] == playlist_id:
            playlist = p
            playlist_index = i
            break
    
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    
    data = request.json
    
    if request.method == 'POST':
        # Add item to playlist
        item = {
            'id': data.get('id'),
            'type': data.get('type'),  # track, show, video
            'added_at': datetime.now().isoformat(),
            'position': len(playlist['items'])
        }
        
        # Check if already in playlist
        if not any(i['id'] == item['id'] and i['type'] == item['type'] for i in playlist['items']):
            playlist['items'].append(item)
            playlist['updated_at'] = datetime.now().isoformat()
            
            users[username]['playlists'][playlist_index] = playlist
            save_users(users)
            
        return jsonify({'success': True, 'item': item})
    
    if request.method == 'DELETE':
        # Remove item from playlist
        item_id = data.get('id')
        item_type = data.get('type')
        
        playlist['items'] = [
            i for i in playlist['items'] 
            if not (i['id'] == item_id and i['type'] == item_type)
        ]
        
        # Reorder positions
        for i, item in enumerate(playlist['items']):
            item['position'] = i
        
        playlist['updated_at'] = datetime.now().isoformat()
        users[username]['playlists'][playlist_index] = playlist
        save_users(users)
        
        return jsonify({'success': True})

@app.route('/api/user/playlists/<playlist_id>/reorder', methods=['POST'])
@auth_required
def reorder_playlist(playlist_id):
    """Reorder playlist items"""
    username = session.get('username')
    users = load_users()
    
    playlist = None
    playlist_index = None
    
    for i, p in enumerate(users[username].get('playlists', [])):
        if p['id'] == playlist_id:
            playlist = p
            playlist_index = i
            break
    
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    
    data = request.json
    new_order = data.get('order', [])  # List of item IDs in new order
    
    # Reorder items based on new_order
    ordered_items = []
    for item_id in new_order:
        for item in playlist['items']:
            if item['id'] == item_id:
                item['position'] = len(ordered_items)
                ordered_items.append(item)
                break
    
    playlist['items'] = ordered_items
    playlist['updated_at'] = datetime.now().isoformat()
    
    users[username]['playlists'][playlist_index] = playlist
    save_users(users)
    
    return jsonify({'success': True, 'playlist': playlist})

@app.route('/api/user/collections', methods=['GET', 'POST'])
@auth_required
def user_collections():
    """User collections - organized folders of content"""
    username = session.get('username')
    users = load_users()
    
    if 'collections' not in users[username]:
        users[username]['collections'] = []
    
    if request.method == 'POST':
        data = request.json
        collection = {
            'id': hashlib.md5(f"{username}-collection-{datetime.now().isoformat()}".encode()).hexdigest()[:8],
            'name': data.get('name'),
            'description': data.get('description', ''),
            'type': data.get('type', 'mixed'),  # mixed, music, shows, artists
            'created_at': datetime.now().isoformat(),
            'items': [],
            'tags': data.get('tags', [])
        }
        
        users[username]['collections'].append(collection)
        save_users(users)
        return jsonify({'success': True, 'collection': collection})
    
    return jsonify(users[username]['collections'])

@app.route('/api/user/likes', methods=['GET', 'POST', 'DELETE'])
@auth_required
def user_likes():
    """Manage user likes"""
    username = session.get('username')
    users = load_users()
    
    if 'likes' not in users[username]:
        users[username]['likes'] = []
    
    if request.method == 'POST':
        data = request.json
        like = {
            'id': data.get('id'),
            'type': data.get('type'),
            'liked_at': datetime.now().isoformat()
        }
        
        # Remove if already liked (unlike)
        users[username]['likes'] = [
            l for l in users[username]['likes'] 
            if not (l['id'] == like['id'] and l['type'] == like['type'])
        ]
        
        # Add like
        users[username]['likes'].append(like)
        save_users(users)
        
        return jsonify({'success': True, 'liked': True})
    
    if request.method == 'DELETE':
        data = request.json
        users[username]['likes'] = [
            l for l in users[username]['likes']
            if not (l['id'] == data.get('id') and l['type'] == data.get('type'))
        ]
        save_users(users)
        return jsonify({'success': True, 'liked': False})
    
    return jsonify(users[username]['likes'])

@app.route('/api/user/history')
@auth_required
def user_history():
    """Get user listening/viewing history"""
    username = session.get('username')
    users = load_users()
    
    return jsonify(users[username].get('history', []))

@app.route('/api/user/history', methods=['POST'])
@auth_required
def add_to_history():
    """Add item to user history"""
    username = session.get('username')
    users = load_users()
    
    if 'history' not in users[username]:
        users[username]['history'] = []
    
    data = request.json
    history_item = {
        'id': data.get('id'),
        'type': data.get('type'),
        'played_at': datetime.now().isoformat(),
        'duration_played': data.get('duration_played', 0)
    }
    
    # Keep only last 100 items
    users[username]['history'] = [history_item] + users[username]['history'][:99]
    save_users(users)
    
    return jsonify({'success': True})

@app.route('/api/user/recommendations')
@auth_required
def user_recommendations():
    """Get personalized recommendations based on user activity"""
    username = session.get('username')
    users = load_users()
    
    user_data = users[username]
    likes = user_data.get('likes', [])
    history = user_data.get('history', [])
    
    # Load all content
    music_data = load_json_data('music.json', {'tracks': []})
    shows_data = load_json_data('shows.json', {'shows': []})
    artists_data = load_json_data('artists.json', {'artists': []})
    
    recommendations = {
        'based_on_likes': [],
        'based_on_history': [],
        'trending': [],
        'similar_artists': []
    }
    
    # Simple recommendation logic - can be made more sophisticated
    liked_artists = [l['id'] for l in likes if l['type'] == 'artist']
    liked_genres = []
    
    # Get tracks from liked artists
    for track in music_data.get('tracks', []):
        if track.get('artist_slug') in liked_artists:
            recommendations['based_on_likes'].append({
                'type': 'track',
                'data': track,
                'reason': f"Because you like {track.get('artist', '')}"
            })
    
    # Add some trending content (most recently added)
    recent_tracks = sorted(
        music_data.get('tracks', []), 
        key=lambda x: x.get('added_date', ''), 
        reverse=True
    )[:10]
    
    for track in recent_tracks:
        recommendations['trending'].append({
            'type': 'track',
            'data': track,
            'reason': 'Trending now'
        })
    
    return jsonify(recommendations)

# User Management (Simple)
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Simple login"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    users = load_users()
    
    if username in users and users[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
        session['username'] = username
        session['user_data'] = users[username]
        return jsonify({'success': True, 'user': users[username]['profile']})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Simple registration"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    users = load_users()
    
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    
    users[username] = {
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'profile': {
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'preferences': {
                'theme': 'default',
                'autoplay': True
            }
        }
    }
    
    save_users(users)
    
    session['username'] = username
    session['user_data'] = users[username]
    
    return jsonify({'success': True, 'user': users[username]['profile']})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user/profile')
@auth_required
def user_profile():
    """Get user profile"""
    return jsonify(session.get('user_data', {}).get('profile', {}))

@app.route('/api/user/favorites', methods=['GET', 'POST'])
@auth_required
def user_favorites():
    """Get/add user favorites"""
    username = session.get('username')
    users = load_users()
    
    if request.method == 'POST':
        data = request.json
        item_id = data.get('id')
        item_type = data.get('type')  # track, show, artist
        
        if 'favorites' not in users[username]:
            users[username]['favorites'] = []
        
        favorite = {
            'id': item_id,
            'type': item_type,
            'added_at': datetime.now().isoformat()
        }
        
        # Remove if already favorited, add if not
        users[username]['favorites'] = [f for f in users[username]['favorites'] if f['id'] != item_id]
        users[username]['favorites'].append(favorite)
        
        save_users(users)
        return jsonify({'success': True})
    
    return jsonify(users[username].get('favorites', []))

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

def find_available_port(start_port=5001, end_port=5010):
    """Find an available port between start_port and end_port"""
    import socket
    for port in range(start_port, end_port + 1):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            # Port is in use, try next one
            continue
    return None

if __name__ == '__main__':
    # Create data directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/data', exist_ok=True)
    
    # Find available port
    port = find_available_port()
    if port is None:
        print("❌ No available ports found between 5001-5010")
        print("💡 Try closing other applications or use a different port range")
        exit(1)
    
    print(f"🎵 Starting Ahoy Indie Media on port {port}...")
    print(f"📍 Server will be available at: http://localhost:{port}")
    
    app.run(debug=True, host='127.0.0.1', port=port)
