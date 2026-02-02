import argparse
import json
import os
import tempfile
from typing import Any, Dict, List, Optional

import requests
from mutagen import File as MutagenFile


DEFAULT_INPUT = os.path.join("static", "data", "music.json")


def download_to_temp(url: str, timeout: float) -> str:
    response = requests.get(url, stream=True, timeout=timeout)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                tmp.write(chunk)
        return tmp.name


def get_duration_seconds(file_path: str) -> Optional[int]:
    audio = MutagenFile(file_path)
    if not audio or not getattr(audio, "info", None):
        return None
    length = getattr(audio.info, "length", None)
    if not length or length <= 0:
        return None
    return int(round(length))


def choose_audio_url(track: Dict[str, Any]) -> Optional[str]:
    return track.get("audio_url") or track.get("preview_url")


def refresh_durations(
    tracks: List[Dict[str, Any]],
    timeout: float,
    force: bool,
    max_tracks: Optional[int],
    dry_run: bool,
) -> Dict[str, int]:
    updated = 0
    skipped = 0
    failed = 0
    processed = 0

    for track in tracks:
        if max_tracks is not None and processed >= max_tracks:
            break
        processed += 1

        current = int(track.get("duration_seconds") or 0)
        if current > 0 and not force:
            skipped += 1
            continue

        url = choose_audio_url(track)
        if not url:
            failed += 1
            continue

        tmp_path = None
        try:
            tmp_path = download_to_temp(url, timeout)
            duration = get_duration_seconds(tmp_path)
            if duration:
                if not dry_run:
                    track["duration_seconds"] = duration
                updated += 1
            else:
                failed += 1
        except Exception:
            failed += 1
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    return {
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
        "processed": processed,
    }


def load_music(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_music(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh duration_seconds in static/data/music.json by scanning audio URLs."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Path to music.json")
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="HTTP timeout per request in seconds"
    )
    parser.add_argument(
        "--force", action="store_true", help="Recompute durations even if set"
    )
    parser.add_argument(
        "--max-tracks",
        type=int,
        default=None,
        help="Limit number of tracks processed",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write changes")
    args = parser.parse_args()

    data = load_music(args.input)
    tracks = data.get("tracks", [])
    if not isinstance(tracks, list):
        raise ValueError("music.json is missing a tracks list")

    stats = refresh_durations(
        tracks=tracks,
        timeout=args.timeout,
        force=args.force,
        max_tracks=args.max_tracks,
        dry_run=args.dry_run,
    )

    if not args.dry_run:
        save_music(args.input, data)

    print(
        "Done. processed={processed} updated={updated} skipped={skipped} failed={failed}".format(
            **stats
        )
    )


if __name__ == "__main__":
    main()
