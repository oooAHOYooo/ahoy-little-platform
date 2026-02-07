"""Database-backed content queries for music, shows, artists, and podcasts.

Each function returns plain dicts/lists matching the exact JSON response shapes
from the original static files. Used by API routes in app.py as a drop-in
replacement for load_json_data().

All functions include a TTL-based in-memory cache to avoid hitting the DB
on every request (mirrors the old 600s JSON file cache).
"""
import logging
from time import time as _now

from db import get_session
from models import (
    Track, Show, ContentArtist, ContentArtistAlbum, ContentArtistAlbumTrack,
    ContentArtistShow, ContentArtistTrack, PodcastShow, PodcastEpisode,
    Event, ContentMerch, ContentVideo, WhatsNewItem,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory cache (same pattern as the old _json_data_cache)
# ---------------------------------------------------------------------------
_cache = {}


def _cached(key, ttl, fn):
    """Return cached result or call fn() and cache it."""
    now = _now()
    if key in _cache:
        val, ts = _cache[key]
        if now - ts < ttl:
            return val
    val = fn()
    _cache[key] = (val, now)
    return val


def invalidate_cache(key=None):
    """Clear one key or the entire content cache."""
    if key:
        _cache.pop(key, None)
    else:
        _cache.clear()


# ---------------------------------------------------------------------------
# Serializers: DB row -> dict matching original JSON shape
# ---------------------------------------------------------------------------

def _serialize_track(t):
    """Convert a Track row to a dict matching music.json track objects."""
    d = {
        'id': t.track_id,
        'title': t.title,
        'artist': t.artist,
        'album': t.album,
        'genre': t.genre,
        'duration_seconds': t.duration_seconds,
        'audio_url': t.audio_url,
        'preview_url': t.preview_url,
        'cover_art': t.cover_art,
        'added_date': t.added_date,
        'tags': t.tags or [],
        'artist_slug': t.artist_slug,
    }
    # Optional fields: only include if truthy (matches original JSON where absent)
    if t.artist_url:
        d['artist_url'] = t.artist_url
    if t.background_image:
        d['background_image'] = t.background_image
    if t.featured:
        d['featured'] = True
    if t.is_new:
        d['new'] = True
    if t.date_added:
        d['date_added'] = t.date_added
    # Merge any extra fields from the catch-all column
    if t.extra_fields:
        d.update(t.extra_fields)
    return d


def _serialize_show(s):
    """Convert a Show row to a dict matching shows.json show objects."""
    d = {
        'id': s.show_id,
        'title': s.title,
        'host': s.host,
        'description': s.description,
        'duration_seconds': s.duration_seconds,
        'video_url': s.video_url,
        'thumbnail': s.thumbnail,
        'published_date': s.published_date,
        'views': s.views,
        'type': s.show_type,
        'is_live': s.is_live,
        'tags': s.tags or [],
        'host_slug': s.host_slug,
        'category': s.category,
    }
    if s.trailer_url:
        d['trailer_url'] = s.trailer_url
    if s.extra_fields:
        d.update(s.extra_fields)
    return d


def _serialize_artist(a, albums_map, shows_map, tracks_map):
    """Convert a ContentArtist row + nested data to a dict matching artists.json."""
    # Determine which fields were in the original JSON
    extra = a.extra_fields or {}
    orig_keys = set(extra.pop('_original_keys', []))

    d = {
        'id': a.artist_id,
        'name': a.name,
        'slug': a.slug,
        'type': a.artist_type,
        'image': a.image,
        'social_links': a.social_links or {},
        'genres': a.genres or [],
        'followers': a.followers,
        'verified': a.verified,
    }
    # Only include these if they were in the original record
    if 'description' in orig_keys:
        d['description'] = a.description
    if 'created_at' in orig_keys:
        d['created_at'] = a.created_at_str
    if 'updated_at' in orig_keys:
        d['updated_at'] = a.updated_at_str
    if a.featured:
        d['featured'] = True

    # Only include nested arrays if present in original
    if 'albums' in orig_keys:
        d['albums'] = []
    if 'shows' in orig_keys:
        d['shows'] = []
    if 'tracks' in orig_keys:
        d['tracks'] = []

    # Albums
    if 'albums' in d:
        for alb in albums_map.get(a.artist_id, []):
            alb_dict = {
                'id': alb['album_id'],
                'title': alb['title'],
                'release_date': alb['release_date'],
                'cover_art': alb['cover_art'],
                'tags': alb['tags'] or [],
                'tracks': alb.get('tracks', []),
            }
            if alb.get('is_new'):
                alb_dict['new'] = True
            if alb.get('extra_fields'):
                alb_dict.update(alb['extra_fields'])
            d['albums'].append(alb_dict)

    # Shows
    if 'shows' in d:
        for sh in shows_map.get(a.artist_id, []):
            sh_dict = {
                'id': sh['show_ref_id'],
                'title': sh['title'],
                'type': sh['show_type'],
                'duration': sh['duration'],
                'category': sh['category'],
                'published_date': sh['published_date'],
            }
            d['shows'].append(sh_dict)

    # Tracks
    if 'tracks' in d:
        for tr in tracks_map.get(a.artist_id, []):
            tr_dict = {
                'id': tr['track_ref_id'],
                'title': tr['title'],
                'album': tr['album'],
                'duration': tr['duration'],
                'genre': tr['genre'],
                'added_date': tr['added_date'],
            }
            d['tracks'].append(tr_dict)

    # Merge extra fields (bio, avatar, cover_image, location, website, etc.)
    if a.extra_fields:
        d.update(a.extra_fields)

    return d


def _serialize_podcast_show(ps, episodes):
    """Convert PodcastShow + episodes to dict matching podcasts.json."""
    return {
        'slug': ps.slug,
        'title': ps.title,
        'description': ps.description,
        'artwork': ps.artwork,
        'last_updated': ps.last_updated,
        'episodes': [
            {
                'id': ep.episode_id,
                'title': ep.title,
                'description': ep.description,
                'date': ep.date,
                'duration': ep.duration,
                'duration_seconds': ep.duration_seconds,
                'audio_url': ep.audio_url,
                'artwork': ep.artwork,
            }
            for ep in episodes
        ],
    }


def _serialize_event(e):
    """Convert Event row to dict matching events.json event objects."""
    d = {
        'id': e.event_id,
        'title': e.title,
        'date': e.date,
        'time': e.time,
        'venue': e.venue,
        'venue_address': e.venue_address,
        'event_type': e.event_type,
        'status': e.status,
        'description': e.description or '',
        'photos': e.photos if e.photos is not None else [],
        'image': e.image or '',
        'rsvp_external_url': e.rsvp_external_url,
        'rsvp_enabled': bool(e.rsvp_enabled),
        'rsvp_limit': e.rsvp_limit,
        'rsvps': [],
    }
    if e.extra_fields:
        d.update(e.extra_fields)
    return d


def _serialize_merch_item(m):
    """Convert ContentMerch row to dict matching data/merch.json item shape."""
    d = {
        'id': m.item_id,
        'name': m.name,
        'image_url': m.image_url or '',
        'price_usd': float(m.price_usd),
        'kind': m.kind or 'merch',
        'available': bool(m.available),
    }
    if m.image_url_back:
        d['image_url_back'] = m.image_url_back
    if m.extra_fields:
        d.update(m.extra_fields)
    return d


def _serialize_video(v):
    """Convert ContentVideo row to dict matching videos.json video objects."""
    d = {
        'id': v.video_id,
        'event_id': v.event_id,
        'title': v.title,
        'description': v.description,
        'url': v.url,
        'duration': v.duration,
        'file_size': v.file_size,
        'format': v.format,
        'status': v.status,
        'upload_date': v.upload_date,
        'thumbnail': v.thumbnail or '',
    }
    if v.extra_fields:
        d.update(v.extra_fields)
    return d


# ---------------------------------------------------------------------------
# Query functions (return dicts ready for jsonify)
# ---------------------------------------------------------------------------

def get_all_tracks(ttl=600):
    """Return {"tracks": [...]} matching /api/music response."""
    def _query():
        with get_session() as session:
            rows = session.query(Track).order_by(Track.position).all()
            return {'tracks': [_serialize_track(t) for t in rows]}
    return _cached('all_tracks', ttl, _query)


def get_all_shows(ttl=600):
    """Return {"shows": [...]} matching /api/shows response."""
    def _query():
        with get_session() as session:
            rows = session.query(Show).order_by(Show.position).all()
            return {'shows': [_serialize_show(s) for s in rows]}
    return _cached('all_shows', ttl, _query)


def get_all_artists(ttl=600):
    """Return {"artists": [...], "total_count": N, "last_updated": "..."} matching /api/artists."""
    def _query():
        with get_session() as session:
            artists = session.query(ContentArtist).order_by(ContentArtist.position).all()
            if not artists:
                return {'artists': [], 'total_count': 0, 'last_updated': ''}

            artist_ids = [a.artist_id for a in artists]

            # Load nested data in bulk
            albums_raw = session.query(ContentArtistAlbum).filter(
                ContentArtistAlbum.artist_id_ref.in_(artist_ids)
            ).order_by(ContentArtistAlbum.position).all()

            album_ids = [alb.album_id for alb in albums_raw]
            album_tracks_raw = session.query(ContentArtistAlbumTrack).filter(
                ContentArtistAlbumTrack.album_id_ref.in_(album_ids)
            ).order_by(ContentArtistAlbumTrack.position).all() if album_ids else []

            shows_raw = session.query(ContentArtistShow).filter(
                ContentArtistShow.artist_id_ref.in_(artist_ids)
            ).order_by(ContentArtistShow.position).all()

            tracks_raw = session.query(ContentArtistTrack).filter(
                ContentArtistTrack.artist_id_ref.in_(artist_ids)
            ).order_by(ContentArtistTrack.position).all()

            # Build lookup maps
            album_tracks_by_album = {}
            for at in album_tracks_raw:
                album_tracks_by_album.setdefault(at.album_id_ref, []).append({
                    'id': at.track_id_ref, 'title': at.title,
                })

            albums_map = {}
            for alb in albums_raw:
                albums_map.setdefault(alb.artist_id_ref, []).append({
                    'album_id': alb.album_id,
                    'title': alb.title,
                    'release_date': alb.release_date,
                    'cover_art': alb.cover_art,
                    'tags': alb.tags,
                    'is_new': alb.is_new,
                    'extra_fields': alb.extra_fields,
                    'tracks': album_tracks_by_album.get(alb.album_id, []),
                })

            shows_map = {}
            for sh in shows_raw:
                shows_map.setdefault(sh.artist_id_ref, []).append({
                    'show_ref_id': sh.show_ref_id,
                    'title': sh.title,
                    'show_type': sh.show_type,
                    'duration': sh.duration,
                    'category': sh.category,
                    'published_date': sh.published_date,
                })

            tracks_map = {}
            for tr in tracks_raw:
                tracks_map.setdefault(tr.artist_id_ref, []).append({
                    'track_ref_id': tr.track_ref_id,
                    'title': tr.title,
                    'album': tr.album,
                    'duration': tr.duration,
                    'genre': tr.genre,
                    'added_date': tr.added_date,
                })

            result_artists = [
                _serialize_artist(a, albums_map, shows_map, tracks_map)
                for a in artists
            ]

            return {
                'artists': result_artists,
                'total_count': len(result_artists),
                'last_updated': artists[0].updated_at_str if artists else '',
            }
    return _cached('all_artists', ttl, _query)


def get_all_podcasts(ttl=600):
    """Return {"shows": [...]} matching /api/podcasts (podcasts.json)."""
    def _query():
        with get_session() as session:
            shows = session.query(PodcastShow).order_by(PodcastShow.position).all()
            if not shows:
                return {'shows': []}
            slugs = [s.slug for s in shows]
            episodes = session.query(PodcastEpisode).filter(
                PodcastEpisode.show_slug.in_(slugs)
            ).order_by(PodcastEpisode.position).all()
            eps_by_show = {}
            for ep in episodes:
                eps_by_show.setdefault(ep.show_slug, []).append(ep)
            return {
                'shows': [
                    _serialize_podcast_show(s, eps_by_show.get(s.slug, []))
                    for s in shows
                ]
            }
    return _cached('all_podcasts', ttl, _query)


def get_tracks_list(ttl=600):
    """Return just the list of track dicts (for daily-playlist, radio, etc.)."""
    return get_all_tracks(ttl).get('tracks', [])


def get_shows_list(ttl=600):
    """Return just the list of show dicts."""
    return get_all_shows(ttl).get('shows', [])


def get_artists_list(ttl=600):
    """Return just the list of artist dicts."""
    return get_all_artists(ttl).get('artists', [])


def get_all_events(ttl=600):
    """Return {"events": [...]} matching events.json."""
    def _query():
        with get_session() as session:
            rows = session.query(Event).order_by(Event.position, Event.date.desc()).all()
            return {'events': [_serialize_event(e) for e in rows]}
    return _cached('all_events', ttl, _query)


def get_all_merch(ttl=600):
    """Return {"items": [...]} matching data/merch.json catalog."""
    def _query():
        with get_session() as session:
            rows = session.query(ContentMerch).order_by(ContentMerch.position).all()
            return {'items': [_serialize_merch_item(m) for m in rows]}
    return _cached('all_merch', ttl, _query)


def get_all_videos(ttl=600):
    """Return {"videos": [...]} matching videos.json."""
    def _query():
        with get_session() as session:
            rows = session.query(ContentVideo).order_by(ContentVideo.position).all()
            return {'videos': [_serialize_video(v) for v in rows]}
    return _cached('all_videos', ttl, _query)


def get_all_whats_new(ttl=600):
    """Return whats_new data structured as {"updates": {year: {month: {section: ...}}}}."""
    def _query():
        with get_session() as session:
            rows = session.query(WhatsNewItem).order_by(
                WhatsNewItem.year.desc(), WhatsNewItem.month, WhatsNewItem.section, WhatsNewItem.position
            ).all()
            updates = {}
            for row in rows:
                yr = updates.setdefault(row.year, {})
                mn = yr.setdefault(row.month, {})
                section_titles = {
                    'music': 'Music Updates', 'videos': 'Video Updates',
                    'artists': 'Artist Updates', 'platform': 'Platform Updates',
                    'merch': 'Merch Updates', 'events': 'Events Updates',
                }
                if row.section not in mn:
                    mn[row.section] = {
                        'title': section_titles.get(row.section, f'{row.section.capitalize()} Updates'),
                        'items': [],
                    }
                item = {
                    'type': row.item_type,
                    'title': row.title,
                    'description': row.description,
                }
                if row.date:
                    item['date'] = row.date
                if row.link:
                    item['link'] = row.link
                if row.link_external:
                    item['link_external'] = row.link_external
                if row.features:
                    item['features'] = row.features
                if row.extra_fields:
                    item.update(row.extra_fields)
                mn[row.section]['items'].append(item)
            return {'updates': updates}
    return _cached('all_whats_new', ttl, _query)
