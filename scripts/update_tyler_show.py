import os
import logging
from db import get_session
from models import PodcastShow, PodcastEpisode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_tyler_show():
    """
    Renames 'Tyler's Show' to 'Tyler Needs a Break'
    and adds Episode 1, 2, and 3.
    """
    show_slug = "tylers-show"
    
    with get_session() as session:
        # 1. Update Show Title
        show = session.query(PodcastShow).filter_by(slug=show_slug).first()
        if show:
            logger.info(f"Renaming show: {show.title} -> Tyler Needs a Break")
            show.title = "Tyler Needs a Break"
        else:
            logger.warning(f"Show with slug '{show_slug}' not found. Creating it.")
            show = PodcastShow(
                slug=show_slug,
                title="Tyler Needs a Break",
                artwork="https://ahoy.ooo/images/Ahoy-Indie-Media-DEFAULT-COVER-A-8.jpg"
            )
            session.add(show)
        
        # 2. Update/Add Episode 1
        # Based on previous research, Episode 1 had ID '36'
        ep1 = session.query(PodcastEpisode).filter_by(episode_id="36").first()
        if ep1:
            logger.info("Updating Episode 1 title.")
            ep1.title = "Episode 1"
        else:
            logger.info("Creating Episode 1.")
            ep1 = PodcastEpisode(
                episode_id="36",
                show_slug=show_slug,
                title="Episode 1",
                description="The inaugural episode of Tyler Needs a Break.",
                date="2026-01-29",
                audio_url="https://storage.googleapis.com/ahoy-podcast-collection/Tylers-Show-Ep1.mp3",
                artwork="https://ahoy.ooo/images/Ahoy-Indie-Media-DEFAULT-COVER-A-8.jpg",
                position=1
            )
            session.add(ep1)
            
        # 3. Add Episode 2
        ep2_id = "tylers-show-ep2"
        ep2 = session.query(PodcastEpisode).filter_by(episode_id=ep2_id).first()
        if not ep2:
            logger.info("Adding Episode 2.")
            ep2 = PodcastEpisode(
                episode_id=ep2_id,
                show_slug=show_slug,
                title="Episode 2",
                description="The second episode of Tyler Needs a Break.",
                date="2026-02-15",
                audio_url="https://storage.googleapis.com/ahoy-podcast-collection/Tylers-Show-Ep2.mp3",
                artwork="https://ahoy.ooo/images/Ahoy-Indie-Media-DEFAULT-COVER-A-8.jpg",
                position=2
            )
            session.add(ep2)
        else:
            logger.info("Episode 2 already exists.")

        # 4. Add Episode 3
        ep3_id = "tylers-show-ep3"
        ep3 = session.query(PodcastEpisode).filter_by(episode_id=ep3_id).first()
        if not ep3:
            logger.info("Adding Episode 3.")
            ep3 = PodcastEpisode(
                episode_id=ep3_id,
                show_slug=show_slug,
                title="Episode 3",
                description="The third episode of Tyler Needs a Break.",
                date="2026-02-23",
                audio_url="https://storage.googleapis.com/ahoy-podcast-collection/Tylers-Show-Ep3.mp3",
                artwork="https://ahoy.ooo/images/Ahoy-Indie-Media-DEFAULT-COVER-A-8.jpg",
                position=3
            )
            session.add(ep3)
        else:
            logger.info("Episode 3 already exists.")

        session.commit()
        logger.info("Show and episodes updated successfully.")

if __name__ == "__main__":
    update_tyler_show()
