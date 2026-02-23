import os
import json
import logging
from google.cloud import storage
from db import get_session
from models import PodcastShow, PodcastEpisode, ContentVideo
import uuid

logger = logging.getLogger(__name__)

def sync_from_gcs(bucket_name, prefix="podcasts/"):
    """
    Prototype: Syncs content metadata from a GCS bucket.
    Assumes files are organized as:
    prefix/show-slug/episode-id.mp3
    prefix/show-slug/episode-id.mp3.json  <- Metadata
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blobs = list(client.list_blobs(bucket, prefix=prefix))
        
        # Group blobs by their "base" path (everything before .json if it's a json file)
        media_files = {}
        metadata_files = {}
        
        for blob in blobs:
            if blob.name.endswith(".json"):
                base = blob.name[:-5]
                metadata_files[base] = blob
            elif blob.name.lower().endswith((".mp3", ".mp4", ".mov", ".wav")):
                media_files[blob.name] = blob
        
        with get_session() as session:
            for media_path, media_blob in media_files.items():
                # Extract show_slug and episode_id from path
                # Expecting prefix/show-slug/episode-id.extension
                parts = media_path[len(prefix):].strip("/").split("/")
                if len(parts) < 2:
                    continue
                
                show_slug = parts[0]
                filename = parts[-1]
                episode_id = filename.rsplit(".", 1)[0]
                
                # Check if we have metadata
                metadata = {}
                if media_path in metadata_files:
                    try:
                        content = metadata_files[media_path].download_as_text()
                        metadata = json.loads(content)
                    except Exception as e:
                        logger.warning(f"Failed to parse metadata for {media_path}: {e}")
                
                # Default values if metadata is missing
                title = metadata.get("title", episode_id.replace("-", " ").title())
                description = metadata.get("description", "")
                date = metadata.get("date", media_blob.updated.strftime("%Y-%m-%d") if media_blob.updated else "")
                
                # Upsert Podcast Episode
                existing_ep = session.query(PodcastEpisode).filter_by(episode_id=episode_id).first()
                if existing_ep:
                    existing_ep.title = title
                    existing_ep.description = description
                    existing_ep.date = date
                    # Only update audio_url if metadata provides it, or use GCS public URL if allowed
                    # For prototype, we use the GCS blob public URL if available
                    existing_ep.audio_url = f"https://storage.googleapis.com/{bucket_name}/{media_path}"
                else:
                    new_ep = PodcastEpisode(
                        episode_id=episode_id,
                        show_slug=show_slug,
                        title=title,
                        description=description,
                        date=date,
                        audio_url=f"https://storage.googleapis.com/{bucket_name}/{media_path}",
                        artwork=metadata.get("artwork", ""),
                        position=metadata.get("position", 0)
                    )
                    session.add(new_ep)
            
            session.commit()
            logger.info("GCS Sync completed successfully.")

    except Exception as e:
        logger.error(f"GCS Sync failed: {e}")
        raise

if __name__ == "__main__":
    # Test script entry point
    bucket = os.getenv("AHOY_GCS_BUCKET")
    if bucket:
        print(f"Starting GCS sync for bucket: {bucket}")
        sync_from_gcs(bucket)
    else:
        print("AHOY_GCS_BUCKET not set. Skipping sync test.")
