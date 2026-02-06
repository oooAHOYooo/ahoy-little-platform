#!/usr/bin/env python3
"""Import content from static/data/*.json into database tables.

Idempotent: safe to run multiple times. Uses upsert logic —
existing rows are updated, new rows are inserted.

Usage:
    python scripts/import_content_from_json.py
"""
import json
import os
import sys

# Allow running from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db import get_session, engine
from models import (
    Track, Show, ContentArtist, ContentArtistAlbum, ContentArtistAlbumTrack,
    ContentArtistShow, ContentArtistTrack, PodcastShow, PodcastEpisode, Base,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dev', 'legacy_json')


def _load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"  SKIP {filename} (not found)")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _upsert(session, model, unique_col, records):
    """Insert or update records. Works with SQLite and PostgreSQL."""
    if not records:
        return 0
    dialect = engine.dialect.name
    count = 0
    for rec in records:
        if dialect == 'sqlite':
            stmt = sqlite_insert(model.__table__).values(**rec)
            stmt = stmt.on_conflict_do_update(
                index_elements=[unique_col],
                set_={k: v for k, v in rec.items() if k != unique_col}
            )
            session.execute(stmt)
        else:
            # PostgreSQL
            from sqlalchemy.dialects.postgresql import insert as pg_insert
            stmt = pg_insert(model.__table__).values(**rec)
            stmt = stmt.on_conflict_do_update(
                index_elements=[unique_col],
                set_={k: v for k, v in rec.items() if k != unique_col}
            )
            session.execute(stmt)
        count += 1
    return count


# Known fields per model — everything else goes into extra_fields
TRACK_KNOWN = {
    'id', 'title', 'artist', 'album', 'genre', 'duration_seconds',
    'audio_url', 'preview_url', 'cover_art', 'added_date', 'tags',
    'artist_slug', 'artist_url', 'background_image', 'featured', 'new',
    'date_added',
}

SHOW_KNOWN = {
    'id', 'title', 'host', 'description', 'duration_seconds', 'video_url',
    'trailer_url', 'thumbnail', 'published_date', 'views', 'type',
    'is_live', 'tags', 'host_slug', 'category',
}

ARTIST_KNOWN = {
    'id', 'name', 'slug', 'type', 'description', 'image', 'social_links',
    'genres', 'albums', 'shows', 'tracks', 'followers', 'verified',
    'featured', 'created_at', 'updated_at',
}


def import_tracks():
    data = _load_json('music.json')
    if not data:
        return
    tracks = data.get('tracks', [])
    print(f"  Importing {len(tracks)} tracks...")

    records = []
    for i, t in enumerate(tracks):
        extra = {k: v for k, v in t.items() if k not in TRACK_KNOWN}
        records.append({
            'track_id': t.get('id', f'song_unknown_{i}'),
            'title': t.get('title', ''),
            'artist': t.get('artist', ''),
            'album': t.get('album', ''),
            'genre': t.get('genre', ''),
            'duration_seconds': t.get('duration_seconds', 0),
            'audio_url': t.get('audio_url', ''),
            'preview_url': t.get('preview_url', ''),
            'cover_art': t.get('cover_art', ''),
            'added_date': t.get('added_date', ''),
            'tags': t.get('tags', []),
            'artist_slug': t.get('artist_slug', ''),
            'artist_url': t.get('artist_url'),
            'background_image': t.get('background_image'),
            'featured': bool(t.get('featured', False)),
            'is_new': bool(t.get('new', False)),
            'date_added': t.get('date_added'),
            'position': i,
            'extra_fields': extra if extra else None,
        })

    with get_session() as session:
        n = _upsert(session, Track, 'track_id', records)
        print(f"  -> {n} tracks upserted")


def import_shows():
    data = _load_json('shows.json')
    if not data:
        return
    shows = data.get('shows', [])
    print(f"  Importing {len(shows)} shows...")

    records = []
    for i, s in enumerate(shows):
        extra = {k: v for k, v in s.items() if k not in SHOW_KNOWN}
        records.append({
            'show_id': s.get('id') or f'show_unknown_{i}',
            'title': s.get('title') or '',
            'host': s.get('host') or '',
            'description': s.get('description') or '',
            'duration_seconds': s.get('duration_seconds'),  # preserve None
            'video_url': s.get('video_url') or '',
            'trailer_url': s.get('trailer_url'),
            'thumbnail': s.get('thumbnail') or '',
            'published_date': s.get('published_date') or '',
            'views': s.get('views') or 0,
            'show_type': s.get('type') or '',
            'is_live': bool(s.get('is_live', False)),
            'tags': s.get('tags') or [],
            'host_slug': s.get('host_slug'),
            'category': s.get('category') or '',
            'position': i,
            'extra_fields': extra if extra else None,
        })

    with get_session() as session:
        n = _upsert(session, Show, 'show_id', records)
        print(f"  -> {n} shows upserted")


def import_artists():
    data = _load_json('artists.json')
    if not data:
        return
    artists = data.get('artists', [])
    print(f"  Importing {len(artists)} artists...")

    artist_records = []
    album_records = []
    album_track_records = []
    show_ref_records = []
    track_ref_records = []

    for i, a in enumerate(artists):
        aid = a.get('id', f'artist_unknown_{i}')
        extra = {k: v for k, v in a.items() if k not in ARTIST_KNOWN}
        # Store original keys so serializer knows which fields to emit
        extra['_original_keys'] = sorted(a.keys())

        artist_records.append({
            'artist_id': aid,
            'name': a.get('name', ''),
            'slug': a.get('slug', ''),
            'artist_type': a.get('type', ''),
            'description': a.get('description', ''),
            'image': a.get('image', ''),
            'social_links': a.get('social_links', {}),
            'genres': a.get('genres', []),
            'followers': a.get('followers', 0),
            'verified': bool(a.get('verified', False)),
            'featured': bool(a.get('featured', False)),
            'created_at_str': a.get('created_at', ''),
            'updated_at_str': a.get('updated_at', ''),
            'position': i,
            'extra_fields': extra if extra else None,
        })

        # Albums
        for j, alb in enumerate(a.get('albums', [])):
            alb_id = alb.get('id', f'album_{aid}_{j}')
            alb_extra = {k: v for k, v in alb.items()
                         if k not in {'id', 'title', 'release_date', 'cover_art', 'tags', 'new', 'tracks'}}
            album_records.append({
                'album_id': alb_id,
                'artist_id_ref': aid,
                'title': alb.get('title', ''),
                'release_date': alb.get('release_date', ''),
                'cover_art': alb.get('cover_art', ''),
                'tags': alb.get('tags', []),
                'is_new': bool(alb.get('new', False)),
                'position': j,
                'extra_fields': alb_extra if alb_extra else None,
            })
            for k, at in enumerate(alb.get('tracks', [])):
                album_track_records.append({
                    'album_id_ref': alb_id,
                    'track_id_ref': at.get('id', ''),
                    'title': at.get('title', ''),
                    'position': k,
                })

        # Show refs
        for j, sh in enumerate(a.get('shows', [])):
            show_ref_records.append({
                'artist_id_ref': aid,
                'show_ref_id': sh.get('id', ''),
                'title': sh.get('title', ''),
                'show_type': sh.get('type', ''),
                'duration': sh.get('duration', 0),
                'category': sh.get('category', ''),
                'published_date': sh.get('published_date', ''),
                'position': j,
            })

        # Track refs
        for j, tr in enumerate(a.get('tracks', [])):
            track_ref_records.append({
                'artist_id_ref': aid,
                'track_ref_id': tr.get('id', ''),
                'title': tr.get('title', ''),
                'album': tr.get('album', ''),
                'duration': tr.get('duration', 0),
                'genre': tr.get('genre', ''),
                'added_date': tr.get('added_date', ''),
                'position': j,
            })

    with get_session() as session:
        n = _upsert(session, ContentArtist, 'artist_id', artist_records)
        print(f"  -> {n} artists upserted")

    with get_session() as session:
        # Clear and re-insert nested data (simpler than upserting composite keys)
        artist_ids = [r['artist_id'] for r in artist_records]
        session.query(ContentArtistAlbumTrack).filter(
            ContentArtistAlbumTrack.album_id_ref.in_(
                session.query(ContentArtistAlbum.album_id).filter(
                    ContentArtistAlbum.artist_id_ref.in_(artist_ids)
                )
            )
        ).delete(synchronize_session=False)
        session.query(ContentArtistAlbum).filter(
            ContentArtistAlbum.artist_id_ref.in_(artist_ids)
        ).delete(synchronize_session=False)
        session.query(ContentArtistShow).filter(
            ContentArtistShow.artist_id_ref.in_(artist_ids)
        ).delete(synchronize_session=False)
        session.query(ContentArtistTrack).filter(
            ContentArtistTrack.artist_id_ref.in_(artist_ids)
        ).delete(synchronize_session=False)

        # Re-insert
        for rec in album_records:
            session.execute(ContentArtistAlbum.__table__.insert().values(**rec))
        for rec in album_track_records:
            session.execute(ContentArtistAlbumTrack.__table__.insert().values(**rec))
        for rec in show_ref_records:
            session.execute(ContentArtistShow.__table__.insert().values(**rec))
        for rec in track_ref_records:
            session.execute(ContentArtistTrack.__table__.insert().values(**rec))

        print(f"  -> {len(album_records)} albums, {len(album_track_records)} album tracks, "
              f"{len(show_ref_records)} show refs, {len(track_ref_records)} track refs inserted")


def import_podcasts():
    data = _load_json('podcasts.json')
    if not data:
        return
    shows = data.get('shows', [])
    print(f"  Importing {len(shows)} podcast shows...")

    show_records = []
    episode_records = []

    for i, s in enumerate(shows):
        slug = s.get('slug', f'podcast_{i}')
        show_records.append({
            'slug': slug,
            'title': s.get('title', ''),
            'description': s.get('description', ''),
            'artwork': s.get('artwork', ''),
            'last_updated': s.get('last_updated', ''),
            'position': i,
        })
        for j, ep in enumerate(s.get('episodes', [])):
            episode_records.append({
                'episode_id': ep.get('id', f'{slug}-{j}'),
                'show_slug': slug,
                'title': ep.get('title', ''),
                'description': ep.get('description', ''),
                'date': ep.get('date', ''),
                'duration': ep.get('duration', ''),
                'duration_seconds': ep.get('duration_seconds', 0),
                'audio_url': ep.get('audio_url', ''),
                'artwork': ep.get('artwork', ''),
                'position': j,
            })

    with get_session() as session:
        n = _upsert(session, PodcastShow, 'slug', show_records)
        print(f"  -> {n} podcast shows upserted")

    with get_session() as session:
        n = _upsert(session, PodcastEpisode, 'episode_id', episode_records)
        print(f"  -> {n} podcast episodes upserted")


def main():
    print("Content Import: JSON -> Database")
    print("=" * 40)

    # Ensure content tables exist (for dev/local use)
    content_tables = [
        Track.__table__, Show.__table__, ContentArtist.__table__,
        ContentArtistAlbum.__table__, ContentArtistAlbumTrack.__table__,
        ContentArtistShow.__table__, ContentArtistTrack.__table__,
        PodcastShow.__table__, PodcastEpisode.__table__,
    ]
    Base.metadata.create_all(engine, tables=content_tables, checkfirst=True)

    print("\n[1/4] Music tracks...")
    import_tracks()

    print("\n[2/4] Shows...")
    import_shows()

    print("\n[3/4] Artists...")
    import_artists()

    print("\n[4/4] Podcasts...")
    import_podcasts()

    print("\nDone! Content imported successfully.")


if __name__ == '__main__':
    main()
