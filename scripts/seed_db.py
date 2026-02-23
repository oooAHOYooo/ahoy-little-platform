#!/usr/bin/env python3
"""
Seed the database from JSON files.

All seeders are idempotent by default (skip records that already exist).
Use --force to wipe and re-seed a content type.

Usage:
    python scripts/seed_db.py                        # seed all, skip existing
    python scripts/seed_db.py --force                # wipe and re-seed everything
    python scripts/seed_db.py --only music events    # seed specific types only
    python scripts/seed_db.py --only podcasts --force
"""

import sys
import os
import argparse
import logging

# Run from project root or scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import read_json
from db import get_session
from models import (
    Track, Show,
    ContentArtist, ContentArtistAlbum, ContentArtistAlbumTrack,
    ContentArtistShow, ContentArtistTrack,
    PodcastShow, PodcastEpisode,
    Event, ContentMerch, ContentVideo, WhatsNewItem,
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s  %(message)s')
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load(filename: str) -> dict:
    """Load JSON from dev/legacy_json/ first, then static/data/."""
    for base in ('dev/legacy_json', 'static/data'):
        path = os.path.join(base, filename)
        if os.path.exists(path):
            return read_json(path, {})
    return {}


def _wipe(session, *models):
    """Delete all rows from the given models (in reverse order for FK safety)."""
    for m in reversed(models):
        session.query(m).delete(synchronize_session=False)
    session.flush()


# ---------------------------------------------------------------------------
# Music
# ---------------------------------------------------------------------------

def seed_music(session, force=False):
    if force:
        _wipe(session, Track)
    tracks = _load('music.json').get('tracks', [])
    added = skipped = 0
    for i, t in enumerate(tracks):
        track_id = t.get('id') or f'track_{i}'
        if session.query(Track).filter_by(track_id=track_id).first():
            skipped += 1
            continue
        session.add(Track(
            track_id=track_id,
            title=t.get('title', ''),
            artist=t.get('artist', ''),
            album=t.get('album', ''),
            genre=t.get('genre', ''),
            duration_seconds=int(t.get('duration_seconds') or 0),
            audio_url=t.get('audio_url', ''),
            preview_url=t.get('preview_url', ''),
            cover_art=t.get('cover_art', ''),
            added_date=t.get('added_date', ''),
            tags=t.get('tags') or [],
            artist_slug=t.get('artist_slug', ''),
            artist_url=t.get('artist_url') or None,
            background_image=t.get('background_image') or None,
            featured=bool(t.get('featured', False)),
            is_new=bool(t.get('new', False)),
            date_added=t.get('date_added') or None,
            position=i,
        ))
        added += 1
    log.info(f'  music     : {added} added, {skipped} skipped')


# ---------------------------------------------------------------------------
# Shows
# ---------------------------------------------------------------------------

def seed_shows(session, force=False):
    if force:
        _wipe(session, Show)
    shows = _load('shows.json').get('shows', [])
    added = skipped = 0
    for i, s in enumerate(shows):
        show_id = s.get('id') or f'show_{i}'
        if session.query(Show).filter_by(show_id=show_id).first():
            skipped += 1
            continue
        session.add(Show(
            show_id=show_id,
            title=s.get('title', ''),
            host=s.get('host', ''),
            description=s.get('description', ''),
            duration_seconds=s.get('duration_seconds') or None,
            video_url=s.get('video_url', ''),
            trailer_url=s.get('trailer_url') or None,
            thumbnail=s.get('thumbnail', ''),
            published_date=s.get('published_date', ''),
            views=int(s.get('views') or 0),
            show_type=s.get('type', ''),
            is_live=bool(s.get('is_live', False)),
            tags=s.get('tags') or [],
            host_slug=s.get('host_slug') or None,
            category=s.get('category', ''),
            position=i,
        ))
        added += 1
    log.info(f'  shows     : {added} added, {skipped} skipped')


# ---------------------------------------------------------------------------
# Artists  (with nested albums, shows, tracks)
# ---------------------------------------------------------------------------

def seed_artists(session, force=False):
    if force:
        _wipe(session,
              ContentArtistAlbumTrack, ContentArtistAlbum,
              ContentArtistShow, ContentArtistTrack,
              ContentArtist)
    artists = _load('artists.json').get('artists', [])
    added = skipped = 0
    for i, a in enumerate(artists):
        artist_id = a.get('id') or f'artist_{i}'
        if session.query(ContentArtist).filter_by(artist_id=artist_id).first():
            skipped += 1
            continue

        # Track which top-level keys were present so _serialize_artist()
        # can reproduce the exact same JSON shape.
        orig_keys = [k for k in
                     ('description', 'created_at', 'updated_at', 'featured',
                      'albums', 'shows', 'tracks')
                     if k in a]

        session.add(ContentArtist(
            artist_id=artist_id,
            name=a.get('name', ''),
            slug=a.get('slug') or artist_id,
            artist_type=a.get('type', ''),
            description=a.get('description', ''),
            image=a.get('image', ''),
            social_links=a.get('social_links') or {},
            genres=a.get('genres') or [],
            followers=int(a.get('followers') or 0),
            verified=bool(a.get('verified', False)),
            featured=bool(a.get('featured', False)),
            created_at_str=a.get('created_at', ''),
            updated_at_str=a.get('updated_at', ''),
            position=i,
            extra_fields={'_original_keys': orig_keys},
        ))

        for j, alb in enumerate(a.get('albums') or []):
            album_id = alb.get('id') or f'{artist_id}_album_{j}'
            session.add(ContentArtistAlbum(
                album_id=album_id,
                artist_id_ref=artist_id,
                title=alb.get('title', ''),
                release_date=alb.get('release_date', ''),
                cover_art=alb.get('cover_art', ''),
                tags=alb.get('tags') or [],
                is_new=bool(alb.get('new', False)),
                position=j,
            ))
            for k, trk in enumerate(alb.get('tracks') or []):
                session.add(ContentArtistAlbumTrack(
                    album_id_ref=album_id,
                    track_id_ref=trk.get('id', ''),
                    title=trk.get('title', ''),
                    position=k,
                ))

        for j, sh in enumerate(a.get('shows') or []):
            session.add(ContentArtistShow(
                artist_id_ref=artist_id,
                show_ref_id=sh.get('id', ''),
                title=sh.get('title', ''),
                show_type=sh.get('type', ''),
                duration=int(sh.get('duration') or 0),
                category=sh.get('category', ''),
                published_date=sh.get('published_date', ''),
                position=j,
            ))

        for j, trk in enumerate(a.get('tracks') or []):
            session.add(ContentArtistTrack(
                artist_id_ref=artist_id,
                track_ref_id=trk.get('id', ''),
                title=trk.get('title', ''),
                album=trk.get('album', ''),
                duration=int(trk.get('duration') or 0),
                genre=trk.get('genre', ''),
                added_date=trk.get('added_date', ''),
                position=j,
            ))

        added += 1
    log.info(f'  artists   : {added} added, {skipped} skipped')


# ---------------------------------------------------------------------------
# Podcasts  (podcasts.json → podcastCollection.json fallback)
# ---------------------------------------------------------------------------

def seed_podcasts(session, force=False):
    if force:
        _wipe(session, PodcastEpisode, PodcastShow)

    data = _load('podcasts.json')
    shows = data.get('shows', [])
    if not shows:
        log.info('  podcasts  : podcasts.json empty, converting podcastCollection.json')
        from services.content_db import _load_podcast_collection_fallback
        shows = _load_podcast_collection_fallback().get('shows', [])

    added = skipped = 0
    for i, s in enumerate(shows):
        slug = s.get('slug') or f'show_{i}'
        if session.query(PodcastShow).filter_by(slug=slug).first():
            skipped += 1
            continue
        session.add(PodcastShow(
            slug=slug,
            title=s.get('title', slug.replace('-', ' ').title()),
            description=s.get('description', ''),
            artwork=s.get('artwork', ''),
            last_updated=s.get('last_updated', ''),
            position=i,
        ))
        for j, ep in enumerate(s.get('episodes') or []):
            ep_id = str(ep.get('id') or f'{slug}_ep_{j}')
            session.add(PodcastEpisode(
                episode_id=ep_id,
                show_slug=slug,
                title=ep.get('title', ''),
                description=ep.get('description', ''),
                date=ep.get('date', ''),
                duration=ep.get('duration', ''),
                duration_seconds=int(ep.get('duration_seconds') or 0),
                audio_url=ep.get('audio_url', ''),
                artwork=ep.get('artwork', ''),
                position=j,
            ))
        added += 1
    log.info(f'  podcasts  : {added} shows added, {skipped} skipped')


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def seed_events(session, force=False):
    if force:
        _wipe(session, Event)
    events = _load('events.json').get('events', [])
    added = skipped = 0
    for i, e in enumerate(events):
        event_id = e.get('id') or f'event_{i}'
        if session.query(Event).filter_by(event_id=event_id).first():
            skipped += 1
            continue
        session.add(Event(
            event_id=event_id,
            title=e.get('title', ''),
            date=e.get('date', ''),
            time=e.get('time', ''),
            venue=e.get('venue', ''),
            venue_address=e.get('venue_address', ''),
            event_type=e.get('event_type', ''),
            status=e.get('status', 'upcoming'),
            description=e.get('description', ''),
            photos=e.get('photos') or [],
            image=e.get('image', ''),
            rsvp_external_url=e.get('rsvp_external_url') or None,
            rsvp_enabled=bool(e.get('rsvp_enabled', True)),
            rsvp_limit=str(e.get('rsvp_limit')) if e.get('rsvp_limit') is not None else None,
            position=i,
        ))
        added += 1
    log.info(f'  events    : {added} added, {skipped} skipped')


# ---------------------------------------------------------------------------
# Merch
# ---------------------------------------------------------------------------

def seed_merch(session, force=False):
    if force:
        _wipe(session, ContentMerch)
    items = _load('merch.json').get('items', [])
    if not items:
        log.info('  merch     : no data (merch.json missing or empty)')
        return
    added = skipped = 0
    for i, m in enumerate(items):
        item_id = m.get('id') or f'merch_{i}'
        if session.query(ContentMerch).filter_by(item_id=item_id).first():
            skipped += 1
            continue
        session.add(ContentMerch(
            item_id=item_id,
            name=m.get('name', ''),
            image_url=m.get('image_url', ''),
            image_url_back=m.get('image_url_back') or None,
            price_usd=float(m.get('price_usd') or 20.0),
            kind=m.get('kind', 'merch'),
            available=bool(m.get('available', True)),
            position=i,
        ))
        added += 1
    log.info(f'  merch     : {added} added, {skipped} skipped')


# ---------------------------------------------------------------------------
# Videos
# ---------------------------------------------------------------------------

def seed_videos(session, force=False):
    if force:
        _wipe(session, ContentVideo)
    videos = _load('videos.json').get('videos', [])
    added = skipped = 0
    for i, v in enumerate(videos):
        video_id = v.get('id') or f'video_{i}'
        if session.query(ContentVideo).filter_by(video_id=video_id).first():
            skipped += 1
            continue
        session.add(ContentVideo(
            video_id=video_id,
            event_id=v.get('event_id') or None,
            title=v.get('title', ''),
            description=v.get('description', ''),
            url=v.get('url') or None,
            duration=str(v.get('duration')) if v.get('duration') else None,
            file_size=str(v.get('file_size')) if v.get('file_size') else None,
            format=v.get('format') or None,
            status=v.get('status', 'coming_soon'),
            upload_date=v.get('upload_date') or None,
            thumbnail=v.get('thumbnail', ''),
            position=i,
        ))
        added += 1
    log.info(f'  videos    : {added} added, {skipped} skipped')


# ---------------------------------------------------------------------------
# What's New
# ---------------------------------------------------------------------------

def seed_whats_new(session, force=False):
    if force:
        _wipe(session, WhatsNewItem)
    updates = _load('whats_new.json').get('updates', {})
    added = skipped = 0
    position = 0
    for year, months in updates.items():
        if not isinstance(months, dict):
            continue
        for month, sections in months.items():
            if not isinstance(sections, dict):
                continue
            for section, content in sections.items():
                if not isinstance(content, dict):
                    continue
                for item in content.get('items') or []:
                    title = item.get('title', '')
                    exists = session.query(WhatsNewItem).filter_by(
                        year=str(year), month=str(month),
                        section=section, title=title,
                    ).first()
                    if exists:
                        skipped += 1
                        continue
                    session.add(WhatsNewItem(
                        year=str(year),
                        month=str(month),
                        section=section,
                        item_type=item.get('type', 'content'),
                        title=title,
                        description=item.get('description', ''),
                        date=item.get('date') or None,
                        link=item.get('link') or None,
                        link_external=item.get('link_external') or None,
                        features=item.get('features') or None,
                        position=position,
                    ))
                    added += 1
                    position += 1
    log.info(f"  whats_new : {added} added, {skipped} skipped")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SEEDERS = {
    'music':     seed_music,
    'shows':     seed_shows,
    'artists':   seed_artists,
    'podcasts':  seed_podcasts,
    'events':    seed_events,
    'merch':     seed_merch,
    'videos':    seed_videos,
    'whats_new': seed_whats_new,
}


def main():
    parser = argparse.ArgumentParser(
        description='Seed the Ahoy database from JSON files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='\n'.join([
            'Content types: ' + ', '.join(SEEDERS.keys()),
            '',
            'Examples:',
            '  python scripts/seed_db.py',
            '  python scripts/seed_db.py --force',
            '  python scripts/seed_db.py --only music events',
            '  python scripts/seed_db.py --only podcasts --force',
        ]),
    )
    parser.add_argument(
        '--force', action='store_true',
        help='Wipe existing records before seeding (re-seed from scratch)',
    )
    parser.add_argument(
        '--only', nargs='+', metavar='TYPE', choices=list(SEEDERS.keys()),
        help='Seed only these content types',
    )
    args = parser.parse_args()

    targets = args.only or list(SEEDERS.keys())
    log.info(f'Seeding: {", ".join(targets)}  (force={args.force})')

    with get_session() as session:
        for name in targets:
            try:
                SEEDERS[name](session, force=args.force)
            except Exception:
                log.exception(f'{name}: FAILED — rolling back')
                raise

    log.info('Done.')


if __name__ == '__main__':
    main()
