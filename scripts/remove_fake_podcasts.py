#!/usr/bin/env python3
"""
Cleanup script to remove fake sample podcast data from the database.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_session
from models import PodcastShow, PodcastEpisode

FAKE_SHOW_SLUGS = ['rob', 'poets-and-friends', 'tyler-broadcast']

def cleanup():
    print("Cleaning up fake podcast data from database...")
    
    with get_session() as session:
        # First, find and delete episodes associated with fake show slugs
        episodes_deleted = session.query(PodcastEpisode).filter(
            PodcastEpisode.show_slug.in_(FAKE_SHOW_SLUGS)
        ).delete(synchronize_session=False)
        
        # Then, delete the shows themselves
        shows_deleted = session.query(PodcastShow).filter(
            PodcastShow.slug.in_(FAKE_SHOW_SLUGS)
        ).delete(synchronize_session=False)
        
        session.commit()
        
        print(f"Deleted {episodes_deleted} episodes.")
        print(f"Deleted {shows_deleted} shows.")
        print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()
