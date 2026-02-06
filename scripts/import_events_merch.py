#!/usr/bin/env python3
"""Import events and merch from JSON into DB (Render-dynamic content).

Reads static/data/events.json and data/merch.json. Idempotent upsert.

Usage:
    python scripts/import_events_merch.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db import get_session, engine
from models import Event, ContentMerch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS_PATH = os.path.join(PROJECT_ROOT, 'static', 'data', 'events.json')
MERCH_PATH = os.path.join(PROJECT_ROOT, 'data', 'merch.json')


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


def import_events():
    if not os.path.exists(EVENTS_PATH):
        print(f"  SKIP events (not found: {EVENTS_PATH})")
        return
    with open(EVENTS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    events = data.get('events', [])
    if not events:
        print("  No events in file")
        return
    print(f"  Importing {len(events)} events...")
    records = []
    for i, e in enumerate(events):
        eid = e.get('id') or str(i)
        if not isinstance(eid, str):
            eid = str(eid)
        records.append({
            'event_id': eid,
            'title': (e.get('title') or '').strip() or 'Untitled',
            'date': e.get('date') or '',
            'time': e.get('time') or '',
            'venue': e.get('venue') or '',
            'venue_address': e.get('venue_address') or '',
            'event_type': e.get('event_type') or '',
            'status': e.get('status') or 'upcoming',
            'description': e.get('description') or '',
            'photos': e.get('photos') if isinstance(e.get('photos'), list) else [],
            'image': e.get('image') or '',
            'rsvp_external_url': e.get('rsvp_external_url'),
            'rsvp_enabled': bool(e.get('rsvp_enabled', True)),
            'rsvp_limit': e.get('rsvp_limit'),
            'position': i,
        })
    with get_session() as session:
        n = _upsert(session, Event, 'event_id', records)
        session.commit()
    print(f"  -> {n} events upserted")


def import_merch():
    if not os.path.exists(MERCH_PATH):
        print(f"  SKIP merch (not found: {MERCH_PATH})")
        return
    with open(MERCH_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data.get('items', []) if isinstance(data, dict) else []
    if not items:
        print("  No merch items in file")
        return
    print(f"  Importing {len(items)} merch items...")
    records = []
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        item_id = it.get('id') or f"item_{i}"
        if not isinstance(item_id, str):
            item_id = str(item_id)
        records.append({
            'item_id': item_id,
            'name': (it.get('name') or '').strip() or 'Item',
            'image_url': it.get('image_url') or '',
            'image_url_back': it.get('image_url_back'),
            'price_usd': float(it.get('price_usd', 20.0)),
            'kind': it.get('kind') or 'merch',
            'available': bool(it.get('available', True)),
            'position': i,
        })
    with get_session() as session:
        n = _upsert(session, ContentMerch, 'item_id', records)
        session.commit()
    print(f"  -> {n} merch items upserted")


def main():
    print("Import events & merch (JSON -> DB)")
    print("=" * 40)
    print("\n[1/2] Events...")
    import_events()
    print("\n[2/2] Merch...")
    import_merch()
    print("\nDone.")


if __name__ == '__main__':
    main()
