import random
import hashlib
from datetime import datetime, timezone

def get_synced_radio_state(tracks):
    """
    Returns the current track and offset based on global server time.
    Ensures all users hear the same track at the same time.
    """
    if not tracks:
        return None

    # Filter out tracks without duration or audio_url
    valid_tracks = [t for t in tracks if (t.get('audio_url') or t.get('preview_url')) and t.get('duration')]
    
    if not valid_tracks:
        # Fallback if no durations, just pick random daily
        if not tracks: return None
        return {
            'track': tracks[0],
            'start_time': datetime.now(timezone.utc).isoformat(),
            'offset_ms': 0
        }

    # Deterministic daily shuffle
    # Use today's date to seed the shuffle so the order is consistent for 24h
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    seed_val = int(hashlib.sha256(today_str.encode('utf-8')).hexdigest()[:8], 16)
    rng = random.Random(seed_val)
    
    shuffled_tracks = list(valid_tracks)
    rng.shuffle(shuffled_tracks)

    # Calculate total playlist duration
    total_duration = sum(t.get('duration', 0) for t in shuffled_tracks)
    if total_duration == 0:
        return None

    # Get current time in seconds (epoch)
    now_ts = datetime.now(timezone.utc).timestamp()
    
    # Global loop position
    # The playlist repeats endlessly. We find where we are in the loop.
    # Align to midnight UTC for clean rotation start (optional, but helps mental model)
    today_start_ts = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    time_since_start = now_ts - today_start_ts
    
    # Position in the playlist loop
    loop_pos = time_since_start % total_duration
    
    # Find which track is at this position
    current_track = None
    elapsed = 0
    track_start_offset = 0
    
    for track in shuffled_tracks:
        duration = track.get('duration', 0)
        if elapsed + duration > loop_pos:
            current_track = track
            track_start_offset = loop_pos - elapsed
            break
        elapsed += duration
        
    # Calculate when this track started
    # It started 'track_start_offset' seconds ago
    track_started_at_ts = now_ts - track_start_offset
    
    return {
        'track': current_track,
        'started_at_ts': track_started_at_ts,
        'offset_seconds': track_start_offset,
        'total_duration': current_track.get('duration', 0),
        'server_time': now_ts,
        'next_tracks': _get_next_tracks(shuffled_tracks, current_track, 5)
    }

def _get_next_tracks(playlist, current, count):
    if not current: return []
    try:
        idx = playlist.index(current)
        # Circular slice
        next_items = []
        for i in range(1, count + 1):
            next_items.append(playlist[(idx + i) % len(playlist)])
        return next_items
    except ValueError:
        return []

