#!/usr/bin/env python3
"""Import podcastCollection.json (flat episode list) into PodcastShow + PodcastEpisode.

Derives show name from episode title and builds shows + episodes. Idempotent upsert.

Usage:
    python scripts/import_podcast_collection.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db import get_session, engine
from models import PodcastShow, PodcastEpisode

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECTION_PATH = os.path.join(PROJECT_ROOT, 'static', 'data', 'podcastCollection.json')

SLUG_ALIASES = {
    'The Rob Show': 'rob',
    'Rob Meglio Show': 'rob',
    'Poets & Friends': 'poets-and-friends',
    "Tyler's New Broadcast": 'tyler-broadcast',
    "Tyler's Show": 'tylers-show',
}


def _slugify(s: str) -> str:
    s = (s or '').strip().lower()
    s = re.sub(r"['']", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s or 'show'


def extract_show_name(title: str) -> str:
    t = (title or '').strip()
    lower = t.lower()
    if lower.startswith('the rob show'):
        return 'The Rob Show'
    if lower.startswith('my friend'):
        return 'My Friend'
    if lower.startswith('found cassettes'):
        return 'Found Cassettes'
    if lower.startswith("tyler's show"):
        return "Tyler's Show"
    head = re.split(r'\s*[-–—]\s*', t, maxsplit=1)[0].strip()
    head = re.sub(r'\s*#\s*\d+.*$', '', head).strip()
    return head or 'Podcast'


def _upsert(session, model, unique_col, records):
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
            from sqlalchemy.dialects.postgresql import insert as pg_insert
            stmt = pg_insert(model.__table__).values(**rec)
            stmt = stmt.on_conflict_do_update(
                index_elements=[unique_col],
                set_={k: v for k, v in rec.items() if k != unique_col}
            )
            session.execute(stmt)
        count += 1
    return count


def main():
    if not os.path.exists(COLLECTION_PATH):
        print(f"Not found: {COLLECTION_PATH}")
        sys.exit(1)
    with open(COLLECTION_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = list(data.get('podcasts', []) or [])
    active = [p for p in items if p.get('active', True)]
    active.sort(key=lambda p: (str(p.get('date') or p.get('releaseDate') or ''), int(p.get('id') or 0)), reverse=True)

    # Build show slug -> show info (title, description, artwork, last_updated)
    shows_map = {}
    episode_rows = []
    for p in active:
        title = p.get('title') or 'Untitled Episode'
        show_name = extract_show_name(title)
        show_slug = SLUG_ALIASES.get(show_name) or _slugify(show_name)
        if show_slug not in shows_map:
            shows_map[show_slug] = {
                'slug': show_slug,
                'title': show_name,
                'description': '',
                'artwork': p.get('thumbnail') or '/static/img/default-cover.jpg',
                'last_updated': p.get('date') or p.get('releaseDate') or '',
                'position': len(shows_map),
            }
        else:
            # Update last_updated if this episode is newer
            d = p.get('date') or p.get('releaseDate') or ''
            if d and (not shows_map[show_slug]['last_updated'] or d > shows_map[show_slug]['last_updated']):
                shows_map[show_slug]['last_updated'] = d
        episode_id = str(p.get('id') or title)
        episode_rows.append({
            'episode_id': episode_id,
            'show_slug': show_slug,
            'title': title,
            'description': p.get('description') or '',
            'date': p.get('date') or p.get('releaseDate') or '',
            'duration': '',
            'duration_seconds': 0,
            'audio_url': p.get('mp3url') or '',
            'artwork': p.get('thumbnail') or '/static/img/default-cover.jpg',
            'position': len(episode_rows),
        })

    show_records = list(shows_map.values())
    print(f"Importing {len(show_records)} podcast shows, {len(episode_rows)} episodes...")

    with get_session() as session:
        n_show = _upsert(session, PodcastShow, 'slug', show_records)
        n_ep = _upsert(session, PodcastEpisode, 'episode_id', episode_rows)
        session.commit()
    print(f"  -> {n_show} shows, {n_ep} episodes upserted")
    print("Done.")


if __name__ == '__main__':
    main()
