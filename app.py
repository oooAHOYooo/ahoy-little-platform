from flask import Flask, render_template, jsonify, request, session, send_from_directory, make_response
import os
import json
import uuid
from datetime import datetime, timedelta
import random
import hashlib
from functools import wraps
from user_manager import user_manager

from dotenv import load_dotenv
load_dotenv()

from config import get_config
from extensions import bcrypt, login_manager, limiter, init_cors
from blueprints.auth import bp as auth_bp
from blueprints.activity import bp as activity_bp
from blueprints.playlists import bp as playlists_bp

app = Flask(__name__)
app.config.from_object(get_config())
bcrypt.init_app(app)
login_manager.init_app(app)
limiter.init_app(app)
init_cors(app)
login_manager.login_view = "auth.login"

# Enable compression (optional)
try:
    from flask_compress import Compress
    Compress(app)
    print("✅ Compression enabled")
except ImportError:
    print("⚠️  Flask-Compress not available, compression disabled")

# Cache configuration
CACHE_TIMEOUT = 300  # 5 minutes

# Simple user management (no external dependencies)
USERS_FILE = 'data/users.json'
ACTIVITY_FILE = 'data/user_activity.json'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(activity_bp)
app.register_blueprint(playlists_bp)

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
    response = make_response(render_template('home.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/music')
def music():
    """Music library page"""
    response = make_response(render_template('music.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/shows')
def shows():
    """Shows/video content page"""
    response = make_response(render_template('shows.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/artists')
def artists():
    """Artists directory page"""
    response = make_response(render_template('artists.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/performances')
def performances():
    """Performances page"""
    response = make_response(render_template('performances.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/player')
def player():
    """Full-screen player page"""
    media_id = request.args.get('id')
    media_type = request.args.get('type', 'music')  # music, show, video
    return render_template('player.html', media_id=media_id, media_type=media_type)

@app.route('/artist/<artist_name>')
def artist_profile(artist_name):
    """Individual artist profile page"""
    # Load artist data
    artists_data = load_json_data('artists.json', {'artists': []})
    artist = None
    
    # Find artist by name (case-insensitive)
    for a in artists_data.get('artists', []):
        if a.get('name', '').lower() == artist_name.lower():
            artist = a
            break
    
    if not artist:
        # Return 404 if artist not found
        return render_template('404.html'), 404
    
    return render_template('artist_detail.html', artist=artist)

@app.route('/my-saves')
def my_saves():
    """My Saves page - user's saved content and playlists"""
    return render_template('my_saves.html')

# API Endpoints
@app.route('/api/now-playing')
def api_now_playing():
    """Get curated now playing feed with 30s previews - randomized on each request"""
    music_data = load_json_data('music.json', {'tracks': []})
    shows_data = load_json_data('shows.json', {'shows': []})
    
    # Combine and curate content for discovery feed
    feed_items = []
    
    # Get all available tracks and shows
    all_tracks = music_data.get('tracks', [])
    all_shows = shows_data.get('shows', [])
    
    # Filter for content with preview URLs
    tracks_with_preview = [t for t in all_tracks if t.get('preview_url')]
    shows_with_preview = [s for s in all_shows if s.get('trailer_url')]
    
    # Randomly select tracks (up to 8)
    selected_tracks = random.sample(tracks_with_preview, min(len(tracks_with_preview), 8))
    for track in selected_tracks:
        feed_items.append({
            'id': track['id'],
            'type': 'music',
            'title': track['title'],
            'artist': track['artist'],
            'preview_url': track['preview_url'],
            'cover_art': track['cover_art'],
            'duration': 30,  # Preview length
            'full_url': track['audio_url'],
            'duration_seconds': track.get('duration_seconds', 180),
            'description': track.get('description', ''),
            'genre': track.get('genre', '')
        })
    
    # Randomly select shows (up to 5)
    selected_shows = random.sample(shows_with_preview, min(len(shows_with_preview), 5))
    for show in selected_shows:
        feed_items.append({
            'id': show['id'],
            'type': 'show',
            'title': show['title'],
            'artist': show.get('host', 'Ahoy Indie Media'),
            'preview_url': show['trailer_url'],
            'cover_art': show['thumbnail'],
            'duration': 30,
            'full_url': show['video_url'],
            'duration_seconds': show.get('duration_seconds', 300),
            'description': show.get('description', ''),
            'genre': show.get('genre', '')
        })
    
    # Shuffle for discovery - this will be different on each request
    random.shuffle(feed_items)
    
    # Limit to 12 items for better performance
    feed_items = feed_items[:12]
    
    return jsonify({'feed': feed_items})

@app.route('/api/weather')
def api_weather():
    """Get weather information for user's location"""
    import requests
    from datetime import datetime
    
    # For demo purposes, we'll use a default location (San Francisco)
    # In a real app, you'd get this from user's location or settings
    lat = request.args.get('lat', '37.7749')
    lon = request.args.get('lon', '-122.4194')
    
    # Mock weather data for demo (in production, use a real weather API)
    weather_conditions = [
        {'condition': 'sunny', 'temp': 72, 'description': 'Sunny', 'icon': '☀️'},
        {'condition': 'cloudy', 'temp': 65, 'description': 'Cloudy', 'icon': '☁️'},
        {'condition': 'rainy', 'temp': 58, 'description': 'Rainy', 'icon': '🌧️'},
        {'condition': 'partly_cloudy', 'temp': 68, 'description': 'Partly Cloudy', 'icon': '⛅'},
        {'condition': 'foggy', 'temp': 62, 'description': 'Foggy', 'icon': '🌫️'}
    ]
    
    # Select random weather for demo
    weather = random.choice(weather_conditions)
    
    return jsonify({
        'temperature': weather['temp'],
        'condition': weather['condition'],
        'description': weather['description'],
        'icon': weather['icon'],
        'location': 'San Francisco, CA',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/agenda')
def api_agenda():
    """Get agenda data for the current day"""
    from datetime import datetime, timedelta
    import random
    
    today = datetime.now()
    
    # Mock agenda items
    agenda_items = [
        {
            'id': 1,
            'time': '09:00',
            'title': 'Morning Music Discovery',
            'description': 'Explore new indie tracks',
            'type': 'music',
            'priority': 'high'
        },
        {
            'id': 2,
            'time': '14:00',
            'title': 'Live Show: Indie Spotlight',
            'description': 'Watch today\'s featured performance',
            'type': 'show',
            'priority': 'medium'
        },
        {
            'id': 3,
            'time': '19:00',
            'title': 'Evening Playlist',
            'description': 'Wind down with curated tracks',
            'type': 'music',
            'priority': 'low'
        }
    ]
    
    # Add some random events
    random_events = [
        {'time': '11:30', 'title': 'Artist Interview', 'description': 'Exclusive artist chat', 'type': 'show'},
        {'time': '16:00', 'title': 'New Release Alert', 'description': 'Fresh tracks just dropped', 'type': 'music'},
        {'time': '20:30', 'title': 'Community Chat', 'description': 'Connect with other fans', 'type': 'community'}
    ]
    
    # Add 1-2 random events
    selected_events = random.sample(random_events, random.randint(1, 2))
    agenda_items.extend(selected_events)
    
    # Sort by time
    agenda_items.sort(key=lambda x: x['time'])
    
    return jsonify({
        'date': today.strftime('%A, %B %d, %Y'),
        'day_of_week': today.strftime('%A'),
        'items': agenda_items
    })

@app.route('/api/user/homepage-layout', methods=['GET', 'POST'])
def api_homepage_layout():
    """Get or save user's custom homepage layout"""
    if request.method == 'GET':
        # Return default layout for now
        default_layout = {
            'widgets': [
                {'id': 'weather', 'position': 0, 'enabled': True},
                {'id': 'agenda', 'position': 1, 'enabled': True},
                {'id': 'featured', 'position': 2, 'enabled': True},
                {'id': 'now_playing', 'position': 3, 'enabled': True},
                {'id': 'quick_actions', 'position': 4, 'enabled': True},
                {'id': 'recent_activity', 'position': 5, 'enabled': True}
            ]
        }
        return jsonify(default_layout)
    
    elif request.method == 'POST':
        # Save user's layout (in a real app, save to database)
        layout_data = request.get_json()
        # For demo, just return success
        return jsonify({'success': True, 'message': 'Layout saved successfully'})

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

@app.route('/api/show/<show_id>')
def api_show(show_id):
    """Get individual show by ID"""
    shows_data = load_json_data('shows.json', {'shows': []})
    show = next((s for s in shows_data.get('shows', []) if s.get('id') == show_id), None)
    
    if not show:
        return jsonify({'error': 'Show not found'}), 404
    
    return jsonify(show)

@app.route('/api/artists')
def api_artists():
    """Get artists directory"""
    artists_data = load_json_data('artists.json', {'artists': []})
    return jsonify(artists_data)

@app.route('/api/performances')
def api_performances():
    """Get performances data"""
    # For now, return shows data as performances
    shows_data = load_json_data('shows.json', {'shows': []})
    performances = []
    
    for show in shows_data.get('shows', []):
        # Convert shows to performances format
        performance = {
            'id': show.get('id'),
            'title': show.get('title'),
            'artist': show.get('host') or show.get('artist'),
            'venue': show.get('venue', 'Unknown Venue'),
            'date': show.get('published_date'),
            'thumbnail': show.get('thumbnail'),
            'video_url': show.get('video_url') or show.get('mp4_link'),
            'description': show.get('description'),
            'category': show.get('category', 'concert'),
            'duration': show.get('duration_seconds', 0),
            'featured': show.get('featured', False)
        }
        performances.append(performance)
    
    return jsonify({'performances': performances})

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

@app.route('/api/artists/<int:artist_id>/music')
def api_artist_music(artist_id):
    """Get artist's music tracks"""
    music_data = load_json_data('music.json', {'tracks': []})
    artists_data = load_json_data('artists.json', {'artists': []})
    
    # Find artist by ID
    artist = None
    for a in artists_data.get('artists', []):
        if a.get('id') == artist_id:
            artist = a
            break
    
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    
    # Get artist's tracks
    artist_tracks = [t for t in music_data.get('tracks', []) if t.get('artist_id') == artist_id or t.get('artist') == artist.get('name')]
    
    return jsonify(artist_tracks)

@app.route('/api/artists/<int:artist_id>/shows')
def api_artist_shows(artist_id):
    """Get artist's shows"""
    shows_data = load_json_data('shows.json', {'shows': []})
    artists_data = load_json_data('artists.json', {'artists': []})
    
    # Find artist by ID
    artist = None
    for a in artists_data.get('artists', []):
        if a.get('id') == artist_id:
            artist = a
            break
    
    if not artist:
        return jsonify({'error': 'Artist not found'}), 404
    
    # Get artist's shows
    artist_shows = [s for s in shows_data.get('shows', []) if s.get('host_id') == artist_id or s.get('host') == artist.get('name')]
    
    return jsonify(artist_shows)

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

# Legacy playlist endpoints - redirect to new enhanced system
@app.route('/api/user/playlists', methods=['GET', 'POST'])
@auth_required
def user_playlists():
    """Legacy playlist endpoint - redirects to new system"""
    return manage_playlists()

@app.route('/api/user/playlists/<playlist_id>', methods=['GET', 'PUT', 'DELETE'])
@auth_required
def manage_playlist_legacy(playlist_id):
    """Legacy playlist management - redirects to new system"""
    return manage_playlist(playlist_id)

@app.route('/api/user/playlists/<playlist_id>/items', methods=['POST', 'DELETE'])
@auth_required
def manage_playlist_items(playlist_id):
    """Legacy playlist items - redirects to new system"""
    if request.method == 'POST':
        return add_to_playlist(playlist_id)
    else:
        return remove_from_playlist(playlist_id)

@app.route('/api/user/playlists/<playlist_id>/reorder', methods=['POST'])
@auth_required
def reorder_playlist(playlist_id):
    """Legacy reorder - not supported in new system"""
    return jsonify({'error': 'Reordering not supported in new system'}), 400

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

# Enhanced User Management
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Enhanced login with user manager"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = user_manager.authenticate_user(username, password)
    
    if user:
        session['username'] = username
        session['user_data'] = user
        return jsonify({'success': True, 'user': user['profile']})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Enhanced registration with user manager"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    display_name = data.get('display_name')
    
    try:
        user = user_manager.create_user(username, password, email, display_name)
        session['username'] = username
        session['user_data'] = user
        return jsonify({'success': True, 'user': user['profile']})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

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

@app.route('/api/user/profile', methods=['PUT'])
@auth_required
def update_user_profile():
    """Update user profile"""
    username = session.get('username')
    data = request.json
    success = user_manager.update_user_profile(username, data)
    
    if success:
        # Update session data
        user = user_manager.get_user(username)
        if user:
            session['user_data'] = user
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update profile'}), 400

@app.route('/api/user/stats')
@auth_required
def get_user_stats():
    """Get user statistics"""
    username = session.get('username')
    stats = user_manager.get_user_stats(username)
    return jsonify(stats)

@app.route('/api/user/playlists')
@auth_required
def get_user_playlists():
    """Get user playlists and playlists"""
    username = session.get('username')
    playlists = user_manager.get_user_playlists(username)
    playlists = user_manager.get_user_playlists(username)
    
    # Combine playlists and playlists
    all_items = []
    for playlist in playlists:
        all_items.append({**playlist, 'type': 'playlist'})
    for playlist in playlists:
        all_items.append({**playlist, 'type': 'playlist'})
    
    # Sort by creation date
    all_items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify(all_items)

# Enhanced Saves and Playlists System
@app.route('/api/saves/save', methods=['POST'])
def save_content():
    """Save content (track, show, artist) - works for both logged in and guest users"""
    username = session.get('username')
    
    if not username:
        # For guest users, use session-based temporary saves
        if 'guest_saves' not in session:
            session['guest_saves'] = []
        
        data = request.json
        content_type = data.get('type')
        content_id = data.get('id')
        content_data = data.get('data', {})
        
        # Check if already saved
        existing_save = next((s for s in session['guest_saves'] if s['id'] == content_id and s['type'] == content_type), None)
        if existing_save:
            return jsonify({'success': True, 'saved': True, 'guest': True})
        
        # Add to guest saves
        save_item = {
            'id': content_id,
            'type': content_type,
            'saved_at': datetime.now().isoformat(),
            'data': content_data
        }
        session['guest_saves'].append(save_item)
        session.modified = True
        
        return jsonify({'success': True, 'saved': True, 'guest': True})
    
    # For logged-in users, use the user manager
    data = request.json
    content_type = data.get('type')  # track, show, artist
    content_id = data.get('id')
    content_data = data.get('data', {})
    
    success = user_manager.save_content(username, content_type, content_id, content_data)
    
    if success:
        return jsonify({'success': True, 'saved': True, 'guest': False})
    else:
        return jsonify({'error': 'Failed to save content'}), 400

@app.route('/api/saves/unsave', methods=['POST'])
def unsave_content():
    """Unsave content - works for both guests and users"""
    username = session.get('username')
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    
    if not username:
        # For guest users, use session-based storage
        if 'guest_saves' not in session:
            session['guest_saves'] = []
        
        # Remove from guest saves
        session['guest_saves'] = [s for s in session['guest_saves'] if not (s['id'] == content_id and s['type'] == content_type)]
        session.modified = True
        
        return jsonify({'success': True, 'saved': False, 'guest': True})
    
    # For logged-in users, use the user manager
    success = user_manager.unsave_content(username, content_type, content_id)
    
    if success:
        return jsonify({'success': True, 'saved': False, 'guest': False})
    else:
        return jsonify({'error': 'Failed to unsave content'}), 400

@app.route('/api/saves/check', methods=['POST'])
def check_saved():
    """Check if content is saved - works for both guests and users"""
    username = session.get('username')
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    
    if not username:
        # For guest users, check session storage
        guest_saves = session.get('guest_saves', [])
        is_saved = any(s['id'] == content_id and s['type'] == content_type for s in guest_saves)
        return jsonify({'saved': is_saved, 'guest': True})
    
    # For logged-in users, use the user manager
    is_saved = user_manager.is_content_saved(username, content_type, content_id)
    return jsonify({'saved': is_saved, 'guest': False})

@app.route('/api/saves/<content_type>')
def get_saved_content(content_type):
    """Get user's saved content - works for both guests and users"""
    username = session.get('username')
    
    if not username:
        # For guest users, get from session
        guest_saves = session.get('guest_saves', [])
        saved_items = [s for s in guest_saves if s['type'] == content_type]
        guest_mode = True
    else:
        # For logged-in users, use the user manager
        saved_items = user_manager.get_saved_content(username, content_type)
        guest_mode = False
    
    # Get full content data for each saved item
    full_content = []
    for item in saved_items:
        content_id = item['id']
        content_data = item.get('data', {})
        
        # Try to get full content from appropriate API
        if content_type == 'track':
            music_data = load_json_data('music.json', {'tracks': []})
            full_item = next((t for t in music_data['tracks'] if t['id'] == content_id), content_data)
        elif content_type == 'show':
            shows_data = load_json_data('shows.json', {'shows': []})
            full_item = next((s for s in shows_data['shows'] if s['id'] == content_id), content_data)
        elif content_type == 'artist':
            artists_data = load_json_data('artists.json', {'artists': []})
            full_item = next((a for a in artists_data['artists'] if a['id'] == content_id), content_data)
        else:
            full_item = content_data
        
        # Add save metadata
        full_item['saved_at'] = item['saved_at']
        full_item['is_guest'] = guest_mode
        full_content.append(full_item)
    
    return jsonify({'content': full_content, 'guest': guest_mode})

@app.route('/api/likes/like', methods=['POST'])
@auth_required
def like_content():
    """Like content"""
    username = session.get('username')
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    content_data = data.get('data', {})
    
    success = user_manager.like_content(username, content_type, content_id, content_data)
    
    if success:
        return jsonify({'success': True, 'liked': True})
    else:
        return jsonify({'error': 'Failed to like content'}), 400

@app.route('/api/likes/unlike', methods=['POST'])
@auth_required
def unlike_content():
    """Unlike content"""
    username = session.get('username')
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    
    success = user_manager.unlike_content(username, content_type, content_id)
    
    if success:
        return jsonify({'success': True, 'liked': False})
    else:
        return jsonify({'error': 'Failed to unlike content'}), 400

@app.route('/api/likes/check', methods=['POST'])
@auth_required
def check_liked():
    """Check if content is liked"""
    username = session.get('username')
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    
    is_liked = user_manager.is_content_liked(username, content_type, content_id)
    return jsonify({'liked': is_liked})

@app.route('/api/likes')
@auth_required
def get_liked_content():
    """Get user's liked content"""
    username = session.get('username')
    user = user_manager.get_user(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    liked_content = user['saves'].get('liked_content', [])
    return jsonify({'liked_content': liked_content})

@app.route('/api/recently-played')
@auth_required
def get_recently_played():
    """Get user's recently played content"""
    username = session.get('username')
    user = user_manager.get_user(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    recently_played = user['saves'].get('recently_played', [])
    return jsonify({'recently_played': recently_played})

# Pinterest-style Boards/Collections System
@app.route('/api/playlists', methods=['GET', 'POST'])
def manage_playlists():
    """Get all playlists or create new playlist - works for both guests and users"""
    username = session.get('username')
    
    if not username:
        # For guest users, use session-based storage
        if 'guest_playlists' not in session:
            session['guest_playlists'] = []
        
        if request.method == 'POST':
            data = request.json
            playlist_id = str(uuid.uuid4())
            playlist = {
                'id': playlist_id,
                'name': data.get('name'),
                'description': data.get('description', ''),
                'color': data.get('color', '#6366f1'),
                'is_public': False,  # Guests can't create public playlists
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'tracks': [],
                'shows': [],
                'artists': [],
                'total_items': 0,
                'cover_art': None,
                'tags': [],
                'is_guest': True
            }
            
            session['guest_playlists'].append(playlist)
            session.modified = True
            
            return jsonify({'success': True, 'playlist': playlist, 'guest': True})
        
        return jsonify({'playlists': session['guest_playlists'], 'guest': True})
    
    # For logged-in users, use the user manager
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        color = data.get('color', '#6366f1')
        is_public = data.get('is_public', False)
        
        playlist_id = user_manager.create_playlist(username, name, description, color, is_public)
        
        if playlist_id:
            playlist = user_manager.get_playlist(username, playlist_id)
            return jsonify({'success': True, 'playlist': playlist, 'guest': False})
        else:
            return jsonify({'error': 'Failed to create playlist'}), 400
    
    playlists = user_manager.get_user_playlists(username)
    return jsonify({'playlists': playlists, 'guest': False})

@app.route('/api/playlists/<playlist_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_playlist(playlist_id):
    """Get, update, or delete specific playlist"""
    username = session.get('username')
    
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    if request.method == 'GET':
        playlist = user_manager.get_playlist(username, playlist_id)
        if playlist:
            return jsonify({'playlist': playlist})
        else:
            return jsonify({'error': 'Playlist not found'}), 404
    
    elif request.method == 'PUT':
        data = request.json
        success = user_manager.update_playlist(username, playlist_id, data)
        
        if success:
            playlist = user_manager.get_playlist(username, playlist_id)
            return jsonify({'success': True, 'playlist': playlist})
        else:
            return jsonify({'error': 'Failed to update playlist'}), 400
    
    elif request.method == 'DELETE':
        success = user_manager.delete_playlist(username, playlist_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete playlist'}), 400

@app.route('/api/playlists/<playlist_id>/add', methods=['POST'])
def add_to_playlist(playlist_id):
    """Add content to playlist - works for both guests and users"""
    username = session.get('username')
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    content_data = data.get('data', {})
    
    if not username:
        # For guest users, use session-based storage
        if 'guest_playlists' not in session:
            session['guest_playlists'] = []
        
        # Find the playlist
        playlist = next((b for b in session['guest_playlists'] if b['id'] == playlist_id), None)
        if not playlist:
            return jsonify({'error': 'Board not found'}), 404
        
        # Check if already in playlist
        content_list = playlist.get(content_type + 's', [])
        if any(item['id'] == content_id for item in content_list):
            return jsonify({'success': True, 'playlist': playlist, 'guest': True, 'message': 'Already in playlist'})
        
        # Add to playlist
        item = {
            'id': content_id,
            'added_at': datetime.now().isoformat(),
            'data': content_data
        }
        
        playlist[content_type + 's'].append(item)
        playlist['total_items'] = sum(len(playlist.get(key, [])) for key in ['tracks', 'shows', 'artists'])
        playlist['updated_at'] = datetime.now().isoformat()
        
        session.modified = True
        
        return jsonify({'success': True, 'playlist': playlist, 'guest': True})
    
    # For logged-in users, use the user manager
    success = user_manager.add_to_playlist(username, playlist_id, content_type, content_id, content_data)
    
    if success:
        playlist = user_manager.get_playlist(username, playlist_id)
        return jsonify({'success': True, 'playlist': playlist, 'guest': False})
    else:
        return jsonify({'error': 'Failed to add to playlist'}), 400

@app.route('/api/playlists/<playlist_id>/remove', methods=['POST'])
def remove_from_playlist(playlist_id):
    """Remove content from playlist"""
    username = session.get('username')
    
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.json
    content_type = data.get('type')
    content_id = data.get('id')
    
    success = user_manager.remove_from_playlist(username, playlist_id, content_type, content_id)
    
    if success:
        playlist = user_manager.get_playlist(username, playlist_id)
        return jsonify({'success': True, 'playlist': playlist})
    else:
        return jsonify({'error': 'Failed to remove from playlist'}), 400

@app.route('/api/migrate-guest-data', methods=['POST'])
@auth_required
def migrate_guest_data():
    """Migrate guest data to user account"""
    username = session.get('username')
    data = request.json
    
    if not username:
        return jsonify({'error': 'Not logged in'}), 401
    
    migrated_items = {
        'saves': 0,
        'playlists': 0,
        'likes': 0
    }
    
    # Migrate guest saves
    if 'guest_saves' in data:
        for save_item in data['guest_saves']:
            success = user_manager.save_content(
                username, 
                save_item['type'], 
                save_item['id'], 
                save_item.get('data', {})
            )
            if success:
                migrated_items['saves'] += 1
    
    # Migrate guest playlists
    if 'guest_playlists' in data:
        for playlist_data in data['guest_playlists']:
            playlist_id = user_manager.create_playlist(
                username,
                playlist_data['name'],
                playlist_data['description'],
                playlist_data['color'],
                False  # Guest playlists become private
            )
            if playlist_id:
                # Add all content from guest playlist
                for content_type in ['tracks', 'shows', 'artists']:
                    for item in playlist_data.get(content_type, []):
                        user_manager.add_to_playlist(
                            username,
                            playlist_id,
                            content_type[:-1],  # Remove 's' from plural
                            item['id'],
                            item.get('data', {})
                        )
                migrated_items['playlists'] += 1
    
    # Migrate guest likes
    if 'guest_likes' in data:
        for like_item in data['guest_likes']:
            success = user_manager.like_content(
                username,
                like_item['type'],
                like_item['id'],
                like_item.get('data', {})
            )
            if success:
                migrated_items['likes'] += 1
    
    return jsonify({
        'success': True,
        'migrated': migrated_items,
        'message': f"Migrated {migrated_items['saves']} saves, {migrated_items['playlists']} playlists, and {migrated_items['likes']} likes"
    })

@app.route('/api/guest-data', methods=['GET'])
def get_guest_data():
    """Get current guest data for migration"""
    if 'username' in session:
        return jsonify({'error': 'User is logged in'}), 400
    
    guest_data = {
        'saves': session.get('guest_saves', []),
        'playlists': session.get('guest_playlists', []),
        'likes': session.get('guest_likes', [])
    }
    
    return jsonify(guest_data)

@app.route('/api/user/favorites', methods=['GET', 'POST'])
@auth_required
def user_favorites():
    """Legacy favorites endpoint - redirects to likes"""
    if request.method == 'POST':
        return like_content()
    else:
        return get_liked_content()

# Policy Routes
@app.route('/privacy')
def privacy_policy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@app.route('/security')
def security_policy():
    """Security Policy page"""
    return render_template('security.html')

@app.route('/terms')
def terms_of_service():
    """Terms of Service page"""
    return render_template('terms.html')

# Debug Routes
@app.route('/debug')
def debug_page():
    """Debug console page"""
    return render_template('debug.html')

@app.route('/api/debug/logs')
def get_debug_logs():
    """Get debug logs"""
    # In a real app, you'd read from log files
    # For now, return some sample logs
    logs = [
        {
            'id': 1,
            'timestamp': '10:30:15',
            'level': 'info',
            'source': 'Server',
            'message': 'Server started successfully',
            'details': None
        },
        {
            'id': 2,
            'timestamp': '10:30:20',
            'level': 'error',
            'source': 'API',
            'message': 'Save operation failed',
            'details': 'Mock error for testing - This is not a real error'
        },
        {
            'id': 3,
            'timestamp': '10:30:25',
            'level': 'warning',
            'source': 'Database',
            'message': 'Session expired',
            'details': 'User session expired after 30 minutes of inactivity'
        }
    ]
    return jsonify({'logs': logs})

@app.route('/api/debug/users')
def get_debug_users():
    """Get user details for debug"""
    try:
        users = user_manager.load_users()
        user_list = []
        for username, user_data in users.items():
            user_list.append({
                'username': username,
                'display_name': user_data.get('display_name', username),
                'email': user_data.get('email', ''),
                'created_at': user_data.get('created_at', ''),
                'last_login': user_data.get('last_login', ''),
                'total_saves': user_data.get('activity', {}).get('total_saves', 0),
                'total_plays': user_data.get('activity', {}).get('total_plays', 0)
            })
        
        # Sort by creation date (newest first)
        user_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'total_users': len(user_list),
            'users': user_list
        })
    except Exception as e:
        return jsonify({'users': [], 'error': str(e)})

@app.route('/api/debug/test-save', methods=['POST'])
def test_save():
    """Test save functionality"""
    try:
        data = request.json
        content_type = data.get('type', 'track')
        content_id = data.get('id', 'test_id')
        content_data = data.get('data', {})
        
        # Test the save functionality
        username = session.get('username')
        
        if not username:
            # Test guest save
            if 'guest_saves' not in session:
                session['guest_saves'] = []
            
            session['guest_saves'].append({
                'type': content_type,
                'id': content_id,
                'data': content_data,
                'saved_at': datetime.now().isoformat()
            })
            session.modified = True
            
            return jsonify({
                'success': True,
                'message': 'Guest save test successful',
                'guest': True
            })
        else:
            # Test user save
            success = user_manager.save_content(username, content_type, content_id, content_data)
            return jsonify({
                'success': success,
                'message': 'User save test successful' if success else 'User save test failed',
                'guest': False
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Save test failed with error'
        }), 500

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

@app.route('/api/debug/sample-accounts')
def debug_sample_accounts():
    """Get sample accounts for testing"""
    sample_accounts = [
        {
            'username': 'musiclover',
            'password': 'music123',
            'display_name': 'Music Lover',
            'email': 'musiclover@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 45,
                'saved_shows': 12,
                'liked_content': 78,
                'playlists': 8
            }
        },
        {
            'username': 'indieexplorer',
            'password': 'indie123',
            'display_name': 'Indie Explorer',
            'email': 'indie@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 23,
                'saved_shows': 18,
                'liked_content': 56,
                'playlists': 5
            }
        },
        {
            'username': 'showbinger',
            'password': 'shows123',
            'display_name': 'Show Binger',
            'email': 'shows@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 12,
                'saved_shows': 35,
                'liked_content': 42,
                'playlists': 3
            }
        },
        {
            'username': 'newuser',
            'password': 'new123',
            'display_name': 'New User',
            'email': 'new@ahoy.com',
            'avatar': '/static/img/default-avatar.png',
            'stats': {
                'saved_tracks': 0,
                'saved_shows': 0,
                'liked_content': 0,
                'playlists': 0
            }
        }
    ]
    
    return jsonify({'accounts': sample_accounts})

@app.route('/api/debug/data/<data_type>')
def debug_data_viewer(data_type):
    """View application data for debugging"""
    if data_type == 'users':
        users = user_manager.users
        return jsonify(users)
    elif data_type == 'music':
        music_data = load_json_data('music.json', {'tracks': []})
        return jsonify(music_data)
    elif data_type == 'shows':
        shows_data = load_json_data('shows.json', {'shows': []})
        return jsonify(shows_data)
    elif data_type == 'artists':
        artists_data = load_json_data('artists.json', {'artists': []})
        return jsonify(artists_data)
    else:
        return jsonify({'error': 'Unknown data type'}), 400

@app.route('/api/debug/status')
def debug_system_status():
    """Get system status for debugging"""
    import os

    status = {
        'timestamp': datetime.now().isoformat(),
        'app': {
            'users_count': len(user_manager.users),
            'session_count': len(session),
            'cache_status': 'active'
        },
        'data_files': {
            'users_file': os.path.exists('data/users.json'),
            'music_file': os.path.exists('static/data/music.json'),
            'shows_file': os.path.exists('static/data/shows.json'),
            'artists_file': os.path.exists('static/data/artists.json')
        }
    }

    return jsonify(status)

@app.route('/search')
def search_page():
    """Search results page"""
    return render_template('search.html')

@app.route('/auth')
def auth_page():
    """Authentication page"""
    return render_template('auth.html')

@app.route('/account')
def account_page():
    """User account/profile page"""
    return render_template('account.html')

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@app.route('/sitemap')
def sitemap_page():
    """Sitemap and app structure documentation page"""
    response = make_response(render_template('sitemap.html'))
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TIMEOUT}'
    return response

@app.route('/admin')
def admin_page():
    """Admin page for user management"""
    # Simple admin check - in production, use proper authentication
    admin_username = session.get('username')
    if not admin_username or admin_username != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return render_template('admin.html')

@app.route('/feedback')
def feedback_page():
    """Feedback form page"""
    return render_template('feedback.html')

@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    """Get all users for admin management"""
    admin_username = session.get('username')
    if not admin_username or admin_username != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    users = user_manager.users
    # Return user list without passwords
    user_list = []
    for username, user_data in users.items():
        user_list.append({
            'username': username,
            'email': user_data.get('email', ''),
            'display_name': user_data.get('display_name', username),
            'created_at': user_data.get('created_at', ''),
            'last_login': user_data.get('last_login', ''),
            'activity': user_data.get('activity', {}),
            'profile': user_data.get('profile', {})
        })
    
    return jsonify({'users': user_list})

@app.route('/api/admin/users/<username>', methods=['DELETE'])
def admin_delete_user(username):
    """Delete a user"""
    admin_username = session.get('username')
    if not admin_username or admin_username != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    if username not in user_manager.users:
        return jsonify({'error': 'User not found'}), 404
    
    # Don't allow admin to delete themselves
    if username == 'admin':
        return jsonify({'error': 'Cannot delete admin user'}), 400
    
    del user_manager.users[username]
    user_manager.save_users()
    
    return jsonify({'success': True, 'message': f'User {username} deleted'})

@app.route('/api/admin/users/<username>/reset-password', methods=['POST'])
def admin_reset_password(username):
    """Reset user password"""
    admin_username = session.get('username')
    if not admin_username or admin_username != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    if username not in user_manager.users:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    new_password = data.get('password')
    if not new_password:
        return jsonify({'error': 'Password required'}), 400
    
    user_manager.users[username]['password'] = user_manager.hash_password(new_password)
    user_manager.save_users()
    
    return jsonify({'success': True, 'message': f'Password reset for {username}'})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.json
        feedback_data = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'username': session.get('username', 'anonymous'),
            'feedback_type': data.get('type', 'general'),
            'rating': data.get('rating', 0),
            'ui_rating': data.get('ui_rating', 0),
            'performance_rating': data.get('performance_rating', 0),
            'content_rating': data.get('content_rating', 0),
            'subject': data.get('subject', ''),
            'message': data.get('message', ''),
            'suggestions': data.get('suggestions', ''),
            'bugs': data.get('bugs', ''),
            'feature_requests': data.get('feature_requests', ''),
            'contact_email': data.get('contact_email', ''),
            'anonymous': data.get('anonymous', False),
            'status': 'new'
        }
        
        # Load existing feedback
        feedback_file = 'data/feedback.json'
        try:
            with open(feedback_file, 'r') as f:
                feedback_list = json.load(f)
        except FileNotFoundError:
            feedback_list = []
        
        # Add new feedback
        feedback_list.append(feedback_data)
        
        # Save feedback
        os.makedirs(os.path.dirname(feedback_file), exist_ok=True)
        with open(feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Thank you for your feedback!'})
        
    except Exception as e:
        print(f"Error submitting feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    """Get feedback (admin only)"""
    admin_username = session.get('username')
    if not admin_username or admin_username != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        feedback_file = 'data/feedback.json'
        with open(feedback_file, 'r') as f:
            feedback_list = json.load(f)
        
        # Sort by timestamp (newest first)
        feedback_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({'feedback': feedback_list})
        
    except FileNotFoundError:
        return jsonify({'feedback': []})
    except Exception as e:
        print(f"Error loading feedback: {e}")
        return jsonify({'error': 'Failed to load feedback'}), 500

@app.route('/api/feedback/<feedback_id>/status', methods=['PUT'])
def update_feedback_status():
    """Update feedback status (admin only)"""
    admin_username = session.get('username')
    if not admin_username or admin_username != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.json
        feedback_id = request.view_args['feedback_id']
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status required'}), 400
        
        feedback_file = 'data/feedback.json'
        with open(feedback_file, 'r') as f:
            feedback_list = json.load(f)
        
        # Find and update feedback
        for feedback in feedback_list:
            if feedback['id'] == feedback_id:
                feedback['status'] = new_status
                feedback['updated_at'] = datetime.now().isoformat()
                break
        else:
            return jsonify({'error': 'Feedback not found'}), 404
        
        # Save updated feedback
        with open(feedback_file, 'w') as f:
            json.dump(feedback_list, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Status updated'})
        
    except Exception as e:
        print(f"Error updating feedback status: {e}")
        return jsonify({'error': 'Failed to update status'}), 500

@app.route('/api/search')
def search_api():
    """Search API endpoint"""
    query = request.args.get('q', '').strip().lower()
    
    if not query:
        return jsonify({'results': []})
    
    results = []
    
    try:
        # Search music
        music_data = load_json_data('music.json', {'tracks': []})
        for track in music_data.get('tracks', []):
            if (query in track.get('title', '').lower() or 
                query in track.get('artist', '').lower() or 
                query in track.get('album', '').lower() or 
                query in track.get('genre', '').lower()):
                results.append({
                    **track,
                    'type': 'music',
                    'id': track.get('id', f"music_{len(results)}")
                })
        
        # Search shows
        shows_data = load_json_data('shows.json', {'shows': []})
        for show in shows_data.get('shows', []):
            if (query in show.get('title', '').lower() or 
                query in show.get('host', '').lower() or 
                query in show.get('description', '').lower()):
                results.append({
                    **show,
                    'type': 'show',
                    'id': show.get('id', f"show_{len(results)}")
                })
        
        # Search artists
        artists_data = load_json_data('artists.json', {'artists': []})
        for artist in artists_data.get('artists', []):
            if (query in artist.get('name', '').lower() or 
                query in artist.get('description', '').lower() or 
                query in ' '.join(artist.get('genres', [])).lower()):
                results.append({
                    **artist,
                    'type': 'artist',
                    'id': artist.get('id', f"artist_{len(results)}")
                })
        
        # Shuffle results for variety
        import random
        random.shuffle(results)
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': 'Search failed'}), 500
    
    return jsonify({'results': results})

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
