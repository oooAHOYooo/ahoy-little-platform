#!/usr/bin/env python3
"""Verify that DB-backed API responses match original JSON files exactly."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module

flask_app = app_module.app

def load_orig(filename):
    with open(f'dev/legacy_json/{filename}') as f:
        return json.load(f)

def compare_dicts(orig, db, path=""):
    diffs = []
    all_keys = sorted(set(list(orig.keys()) + list(db.keys())))
    for k in all_keys:
        p = f"{path}.{k}"
        if k not in orig:
            diffs.append(f"  EXTRA in DB: {p} = {repr(db[k])[:80]}")
        elif k not in db:
            diffs.append(f"  MISSING from DB: {p} (orig={repr(orig[k])[:80]})")
        elif orig[k] != db[k]:
            if isinstance(orig[k], dict) and isinstance(db[k], dict):
                diffs.extend(compare_dicts(orig[k], db[k], p))
            elif isinstance(orig[k], list) and isinstance(db[k], list):
                if len(orig[k]) != len(db[k]):
                    diffs.append(f"  LENGTH MISMATCH: {p} orig={len(orig[k])} db={len(db[k])}")
                else:
                    for i, (oi, di) in enumerate(zip(orig[k], db[k])):
                        if isinstance(oi, dict) and isinstance(di, dict):
                            diffs.extend(compare_dicts(oi, di, f"{p}[{i}]"))
                        elif oi != di:
                            diffs.append(f"  VALUE DIFF: {p}[{i}] orig={repr(oi)[:60]} db={repr(di)[:60]}")
            else:
                diffs.append(f"  VALUE DIFF: {p} orig={repr(orig[k])[:60]} db={repr(db[k])[:60]}")
    return diffs

with flask_app.test_client() as client:
    # Music
    print("=== /api/music ===")
    orig = load_orig('music.json')
    db = client.get('/api/music').get_json()
    print(f"Tracks: orig={len(orig['tracks'])}, db={len(db['tracks'])}")
    all_diffs = []
    for i, (ot, dt) in enumerate(zip(orig['tracks'], db['tracks'])):
        diffs = compare_dicts(ot, dt, f"tracks[{i}]")
        all_diffs.extend(diffs)
    if all_diffs:
        print(f"DIFFS FOUND ({len(all_diffs)}):")
        for d in all_diffs[:20]:
            print(d)
    else:
        print("PASS: All tracks match exactly")

    # Shows
    print("\n=== /api/shows ===")
    orig = load_orig('shows.json')
    db = client.get('/api/shows').get_json()
    print(f"Shows: orig={len(orig['shows'])}, db={len(db['shows'])}")
    all_diffs = []
    for i, (os_, ds) in enumerate(zip(orig['shows'], db['shows'])):
        diffs = compare_dicts(os_, ds, f"shows[{i}]")
        all_diffs.extend(diffs)
    if all_diffs:
        print(f"DIFFS FOUND ({len(all_diffs)}):")
        for d in all_diffs[:20]:
            print(d)
    else:
        print("PASS: All shows match exactly")

    # Artists
    print("\n=== /api/artists ===")
    orig = load_orig('artists.json')
    db = client.get('/api/artists').get_json()
    print(f"Artists: orig={len(orig['artists'])}, db={len(db['artists'])}")
    all_diffs = []
    for i, (oa, da) in enumerate(zip(orig['artists'], db['artists'])):
        diffs = compare_dicts(oa, da, f"artists[{i}]")
        all_diffs.extend(diffs)
    if all_diffs:
        print(f"DIFFS FOUND ({len(all_diffs)}):")
        for d in all_diffs[:30]:
            print(d)
    else:
        print("PASS: All artists match exactly")
