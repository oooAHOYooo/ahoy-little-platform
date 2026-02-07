#!/usr/bin/env python3
"""Import videos and what's-new from JSON into DB (Render-dynamic content).

Reads static/data/videos.json and static/data/whats_new.json. Idempotent upsert.

Usage:
    python scripts/import_videos_whats_new.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db import get_session, engine
from models import ContentVideo, WhatsNewItem

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_PATH = os.path.join(PROJECT_ROOT, 'static', 'data', 'videos.json')
WHATS_NEW_PATH = os.path.join(PROJECT_ROOT, 'static', 'data', 'whats_new.json')


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


def import_videos():
    if not os.path.exists(VIDEOS_PATH):
        print(f"  SKIP videos (not found: {VIDEOS_PATH})")
        return
    with open(VIDEOS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    videos = data.get('videos', [])
    if not videos:
        print("  No videos in file")
        return
    print(f"  Importing {len(videos)} videos...")
    records = []
    for i, v in enumerate(videos):
        vid = v.get('id') or str(i)
        if not isinstance(vid, str):
            vid = str(vid)
        records.append({
            'video_id': vid,
            'event_id': v.get('event_id'),
            'title': (v.get('title') or '').strip() or 'Untitled',
            'description': v.get('description') or '',
            'url': v.get('url'),
            'duration': v.get('duration'),
            'file_size': v.get('file_size'),
            'format': v.get('format'),
            'status': v.get('status') or 'coming_soon',
            'upload_date': v.get('upload_date'),
            'thumbnail': v.get('thumbnail') or '',
            'position': i,
        })
    with get_session() as session:
        n = _upsert(session, ContentVideo, 'video_id', records)
        session.commit()
    print(f"  -> {n} videos upserted")


def import_whats_new():
    if not os.path.exists(WHATS_NEW_PATH):
        print(f"  SKIP whats_new (not found: {WHATS_NEW_PATH})")
        return
    with open(WHATS_NEW_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    updates = data.get('updates', {})
    if not updates:
        print("  No updates in file")
        return

    # WhatsNewItem doesn't have a natural unique column for upsert,
    # so we clear and re-insert (idempotent).
    total = 0
    with get_session() as session:
        session.query(WhatsNewItem).delete()
        for year, months in updates.items():
            if not isinstance(months, dict):
                continue
            for month, sections in months.items():
                if not isinstance(sections, dict):
                    continue
                for section_name, section_data in sections.items():
                    if not isinstance(section_data, dict):
                        continue
                    items = section_data.get('items', [])
                    for pos, item in enumerate(items):
                        if not isinstance(item, dict):
                            continue
                        # Collect known fields, put the rest in extra_fields
                        known_keys = {'type', 'title', 'description', 'date', 'link', 'link_external', 'features'}
                        extra = {k: v for k, v in item.items() if k not in known_keys}
                        session.add(WhatsNewItem(
                            year=str(year),
                            month=month.lower(),
                            section=section_name.lower(),
                            item_type=item.get('type') or 'content',
                            title=(item.get('title') or '').strip() or 'Update',
                            description=item.get('description') or '',
                            date=item.get('date'),
                            link=item.get('link'),
                            link_external=item.get('link_external'),
                            features=item.get('features'),
                            position=pos,
                            extra_fields=extra if extra else None,
                        ))
                        total += 1
        session.commit()
    print(f"  -> {total} what's new items imported")


def main():
    print("Import videos & what's new (JSON -> DB)")
    print("=" * 40)
    print("\n[1/2] Videos...")
    import_videos()
    print("\n[2/2] What's New...")
    import_whats_new()
    print("\nDone.")


if __name__ == '__main__':
    main()
