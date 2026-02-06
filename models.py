from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    Boolean,
    JSON,
    BigInteger,
    Numeric,
    Float,
)
from sqlalchemy.orm import declarative_base, relationship
import uuid
from flask_login import UserMixin


Base = declarative_base()


class User(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    # Public handle used across the UI. Lowercase, URL-safe-ish. Added via Alembic migration 0012.
    username = Column(String(64), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False, server_default='false', index=True)
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(String(1024), nullable=True)
    preferences = Column(JSON, nullable=False, default=dict)
    last_active_at = Column(DateTime(timezone=True), nullable=True, index=True)
    disabled = Column(Boolean, nullable=False, default=False, server_default='false', index=True)
    wallet_balance = Column(Numeric(10, 2), nullable=False, default=0, server_default='0.00')
    stripe_customer_id = Column(String(255), nullable=True, unique=True, index=True)  # Stripe Customer ID

    playlists = relationship('Playlist', back_populates='user', cascade='all, delete-orphan')
    bookmarks = relationship('Bookmark', back_populates='user', cascade='all, delete-orphan')
    play_history = relationship('PlayHistory', back_populates='user', cascade='all, delete-orphan')

    @property
    def is_active(self) -> bool:
        # Flask-Login uses this to decide if a user account can authenticate.
        return not bool(self.disabled)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} admin={self.is_admin}>"


class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship('User', back_populates='playlists')
    items = relationship('PlaylistItem', back_populates='playlist', cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_playlists_user_id_created_at', 'user_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Playlist id={self.id} user_id={self.user_id} name={self.name}>"


class PlaylistItem(Base):
    __tablename__ = 'playlist_items'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey('playlists.id', ondelete='CASCADE'), nullable=False, index=True)
    media_id = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)
    position = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    playlist = relationship('Playlist', back_populates='items')

    __table_args__ = (
        Index('ix_playlist_items_playlist_id_position', 'playlist_id', 'position'),
    )

    def __repr__(self) -> str:
        return (
            f"<PlaylistItem id={self.id} playlist_id={self.playlist_id} media={self.media_type}:{self.media_id} "
            f"position={self.position}>"
        )


class Bookmark(Base):
    __tablename__ = 'bookmarks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    media_id = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship('User', back_populates='bookmarks')

    __table_args__ = (
        UniqueConstraint('user_id', 'media_id', 'media_type', name='uq_bookmarks_user_media'),
        Index('ix_bookmarks_user_id_created_at', 'user_id', 'created_at'),
        Index('ix_bookmarks_user_id_media_id', 'user_id', 'media_id'),
    )

    def __repr__(self) -> str:
        return f"<Bookmark id={self.id} user_id={self.user_id} media={self.media_type}:{self.media_id}>"


class PlayHistory(Base):
    __tablename__ = 'play_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    media_id = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress_seconds = Column(Integer, default=0, nullable=False)

    user = relationship('User', back_populates='play_history')

    __table_args__ = (
        Index('ix_play_history_user_id_created_at', 'user_id', 'played_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<PlayHistory id={self.id} user_id={self.user_id} media={self.media_type}:{self.media_id} "
            f"played_at={self.played_at} progress={self.progress_seconds}s>"
        )


class ListeningSession(Base):
    __tablename__ = 'listening_sessions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    media_type = Column(String(20), nullable=False)  # track|episode|clip|short|album|playlist
    media_id = Column(String(36), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    seconds = Column(Integer, nullable=False, default=0)
    source = Column(String(20), nullable=False, default='manual')  # radio|manual
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_listening_sessions_user_id_started_at', 'user_id', 'started_at'),
        Index('ix_listening_sessions_media', 'media_type', 'media_id'),
    )


class ListeningTotal(Base):
    __tablename__ = 'listening_totals'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    total_seconds = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    message = Column(String(2000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_feedback_user_id_created_at', 'user_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} user_id={self.user_id} created_at={self.created_at}>"


class RadioPrefs(Base):
    __tablename__ = 'radio_prefs'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    shuffle = Column(Boolean, nullable=False, default=True, server_default='true')
    include_shows = Column(Boolean, nullable=False, default=True, server_default='true')
    seed_tags = Column(JSON, nullable=False, default=list)  # JSONB on Postgres via migration
    last_station_key = Column(String(255), nullable=True)


# Removed: Achievement and UserAchievement models (gamify feature removed)


# Quest system models removed - see omit/futures_quest_system.py for archived code


class Tip(Base):
    __tablename__ = 'tips'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    artist_id = Column(String(255), nullable=False, index=True)  # Artist slug or ID from JSON
    
    # Tip amount (artist receives 100% of this)
    amount = Column(Numeric(10, 2), nullable=False)  # Tip amount in USD
    
    # Legacy fields (for backward compatibility)
    fee = Column(Numeric(10, 2), nullable=True)  # Platform fee - legacy name
    platform_fee = Column(Numeric(10, 2), nullable=True)  # Platform fee (7.5%)
    net_amount = Column(Numeric(10, 2), nullable=True)  # Amount after fee (legacy)
    
    # New fee structure fields
    stripe_fee = Column(Numeric(10, 2), nullable=True)  # Stripe processing fee (2.9% + $0.30)
    total_paid = Column(Numeric(10, 2), nullable=True)  # Total amount tipper paid (tipAmount + stripeFee + platformFee)
    artist_payout = Column(Numeric(10, 2), nullable=True)  # Amount artist receives (100% of tipAmount)
    platform_revenue = Column(Numeric(10, 2), nullable=True)  # Platform revenue (platformFee)
    
    # Stripe identifiers
    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True, index=True)
    stripe_checkout_session_id = Column(String(255), nullable=True, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('ix_tips_user_id_created_at', 'user_id', 'created_at'),
        Index('ix_tips_artist_id_created_at', 'artist_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Tip id={self.id} user_id={self.user_id} artist_id={self.artist_id} amount={self.amount} total_paid={self.total_paid}>"

    @property
    def boost_amount(self):
        return self.amount

    @boost_amount.setter
    def boost_amount(self, value):
        self.amount = value


class UserArtistFollow(Base):
    __tablename__ = 'user_artist_follows'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    artist_id = Column(String(255), nullable=False, index=True)  # Artist slug or ID from JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'artist_id', name='uq_user_artist_follow_once'),
        Index('ix_user_artist_follows_user_id_created_at', 'user_id', 'created_at'),
        Index('ix_user_artist_follows_artist_id', 'artist_id'),
    )

    def __repr__(self) -> str:
        return f"<UserArtistFollow id={self.id} user_id={self.user_id} artist_id={self.artist_id}>"


class UserArtistPosition(Base):
    __tablename__ = 'user_artist_positions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    artist_id = Column(String(255), nullable=False, index=True)  # Artist slug or ID from JSON
    total_contributed = Column(Numeric(10, 2), nullable=False, default=0)  # Total amount contributed
    last_tip = Column(DateTime, nullable=True)  # Last tip datetime
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'artist_id', name='uq_user_artist_position_once'),
        Index('ix_user_artist_positions_user_id', 'user_id'),
        Index('ix_user_artist_positions_artist_id', 'artist_id'),
        Index('ix_user_artist_positions_user_id_updated_at', 'user_id', 'updated_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<UserArtistPosition id={self.id} user_id={self.user_id} artist_id={self.artist_id} "
            f"total_contributed={self.total_contributed}>"
        )

    @property
    def boost_datetime(self):
        return self.last_tip

    @boost_datetime.setter
    def boost_datetime(self, value):
        self.last_tip = value


class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)  # tip|merch|ticket
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    artist_id = Column(String(50), nullable=True, index=True)
    item_id = Column(String(50), nullable=True, index=True)
    qty = Column(Integer, nullable=False, default=1)
    amount = Column(Numeric(10, 2), nullable=False)         # amount before fees
    total = Column(Numeric(10, 2), nullable=False)          # final charge
    stripe_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Shipping address fields
    shipping_name = Column(String(255), nullable=True)
    shipping_line1 = Column(String(255), nullable=True)
    shipping_line2 = Column(String(255), nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_state = Column(String(50), nullable=True)
    shipping_postal_code = Column(String(20), nullable=True)
    shipping_country = Column(String(2), nullable=True)

    # Fulfillment tracking
    tracking_number = Column(String(100), nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('ix_purchases_user_id_created_at', 'user_id', 'created_at'),
        Index('ix_purchases_type_created_at', 'type', 'created_at'),
    )


class ArtistTip(Base):
    __tablename__ = 'artist_tips'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    artist_name = Column(String(255), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # Amount in cents
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('ix_artist_tips_user_id_created_at', 'user_id', 'created_at'),
        Index('ix_artist_tips_artist_name', 'artist_name'),
    )

    def __repr__(self) -> str:
        return f"<ArtistTip id={self.id} user_id={self.user_id} artist_name={self.artist_name} amount={self.amount}>"


class WalletTransaction(Base):
    __tablename__ = 'wallet_transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # 'fund', 'spend', 'refund'
    amount = Column(Numeric(10, 2), nullable=False)
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    reference_id = Column(String(255), nullable=True, index=True)  # Stripe session ID, purchase ID, etc.
    reference_type = Column(String(50), nullable=True)  # 'stripe_checkout', 'purchase', 'boost', etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index('ix_wallet_transactions_user_id_created_at', 'user_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<WalletTransaction id={self.id} user_id={self.user_id} type={self.type} "
            f"amount={self.amount} balance_after={self.balance_after}>"
        )


class ArtistPayout(Base):
    __tablename__ = 'artist_payouts'

    id = Column(Integer, primary_key=True)
    artist_id = Column(String(255), nullable=False, index=True)  # Artist slug or ID
    amount = Column(Numeric(10, 2), nullable=False)  # Amount to pay out
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    stripe_transfer_id = Column(String(255), nullable=True, unique=True, index=True)  # Stripe Transfer ID if using Stripe Connect
    stripe_payout_id = Column(String(255), nullable=True, index=True)  # Stripe Payout ID
    payment_method = Column(String(50), nullable=True)  # stripe_connect, manual, bank_transfer, etc.
    payment_reference = Column(String(255), nullable=True)  # Reference number for manual payments
    notes = Column(String(1000), nullable=True)  # Notes about the payout
    related_tip_ids = Column(JSON, nullable=True)  # Array of Tip IDs included in this payout
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('ix_artist_payouts_artist_id_status', 'artist_id', 'status'),
        Index('ix_artist_payouts_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return (
            f"<ArtistPayout id={self.id} artist_id={self.artist_id} amount={self.amount} "
            f"status={self.status}>"
        )


class ArtistClaim(Base):
    """
    Links a user account to an artist profile.
    Allows artists to claim their profile and access their dashboard.
    """
    __tablename__ = 'artist_claims'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    artist_id = Column(String(255), nullable=False, unique=True, index=True)  # Artist slug from JSON
    artist_name = Column(String(255), nullable=True)  # Cached artist name
    status = Column(String(50), nullable=False, default='pending', index=True)  # pending, verified, rejected
    verification_code = Column(String(100), nullable=True)  # Code for verification
    stripe_account_id = Column(String(255), nullable=True, index=True)  # Stripe Connect account ID
    payout_email = Column(String(255), nullable=True)  # Email for payouts if not using Stripe Connect
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    verified_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'artist_id', name='uq_artist_claim_user_artist'),
        Index('ix_artist_claims_user_id_status', 'user_id', 'status'),
    )

    def __repr__(self) -> str:
        return f"<ArtistClaim id={self.id} user_id={self.user_id} artist_id={self.artist_id} status={self.status}>"


# ---------------------------------------------------------------------------
# Content tables (migrated from static/data/*.json)
# ---------------------------------------------------------------------------

class Track(Base):
    """Music track — source of truth for /api/music."""
    __tablename__ = 'content_tracks'

    id = Column(Integer, primary_key=True)
    track_id = Column(String(50), unique=True, nullable=False, index=True)  # "song_1"
    title = Column(String(500), nullable=False, default='')
    artist = Column(String(255), nullable=False, default='')
    album = Column(String(255), nullable=False, default='')
    genre = Column(String(100), nullable=False, default='')
    duration_seconds = Column(Integer, nullable=False, default=0)
    audio_url = Column(String(1024), nullable=False, default='')
    preview_url = Column(String(1024), nullable=False, default='')
    cover_art = Column(String(1024), nullable=False, default='')
    added_date = Column(String(50), nullable=False, default='')
    tags = Column(JSON, nullable=False, default=list)
    artist_slug = Column(String(255), nullable=False, default='', index=True)
    artist_url = Column(String(1024), nullable=True)
    background_image = Column(String(1024), nullable=True)
    featured = Column(Boolean, nullable=False, default=False)
    is_new = Column(Boolean, nullable=False, default=False)  # JSON field "new"
    date_added = Column(String(50), nullable=True)  # alternate date format
    position = Column(Integer, nullable=False, default=0, index=True)
    extra_fields = Column(JSON, nullable=True)


class Show(Base):
    """Video show/episode — source of truth for /api/shows."""
    __tablename__ = 'content_shows'

    id = Column(Integer, primary_key=True)
    show_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, default='')
    host = Column(String(255), nullable=False, default='')
    description = Column(String(5000), nullable=False, default='')
    duration_seconds = Column(Integer, nullable=True)  # Some shows have null
    video_url = Column(String(1024), nullable=False, default='')
    trailer_url = Column(String(1024), nullable=True)
    thumbnail = Column(String(1024), nullable=False, default='')
    published_date = Column(String(50), nullable=False, default='')
    views = Column(Integer, nullable=False, default=0)
    show_type = Column(String(50), nullable=False, default='')  # JSON "type"
    is_live = Column(Boolean, nullable=False, default=False)
    tags = Column(JSON, nullable=False, default=list)
    host_slug = Column(String(255), nullable=True, index=True)
    category = Column(String(100), nullable=False, default='')
    position = Column(Integer, nullable=False, default=0, index=True)
    extra_fields = Column(JSON, nullable=True)


class ContentArtist(Base):
    """Artist profile — source of truth for /api/artists."""
    __tablename__ = 'content_artists'

    id = Column(Integer, primary_key=True)
    artist_id = Column(String(50), unique=True, nullable=False, index=True)  # "artist_17"
    name = Column(String(255), nullable=False, default='')
    slug = Column(String(255), unique=True, nullable=False, index=True)
    artist_type = Column(String(50), nullable=False, default='')  # JSON "type"
    description = Column(String(5000), nullable=False, default='')
    image = Column(String(1024), nullable=False, default='')
    social_links = Column(JSON, nullable=False, default=dict)
    genres = Column(JSON, nullable=False, default=list)
    followers = Column(Integer, nullable=False, default=0)
    verified = Column(Boolean, nullable=False, default=False)
    featured = Column(Boolean, nullable=False, default=False)
    created_at_str = Column(String(50), nullable=False, default='')  # JSON "created_at"
    updated_at_str = Column(String(50), nullable=False, default='')  # JSON "updated_at"
    position = Column(Integer, nullable=False, default=0, index=True)
    extra_fields = Column(JSON, nullable=True)  # bio, avatar, cover_image, location, etc.


class ContentArtistAlbum(Base):
    """Album nested inside an artist record."""
    __tablename__ = 'content_artist_albums'

    id = Column(Integer, primary_key=True)
    album_id = Column(String(100), unique=True, nullable=False, index=True)
    artist_id_ref = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False, default='')
    release_date = Column(String(50), nullable=False, default='')
    cover_art = Column(String(1024), nullable=False, default='')
    tags = Column(JSON, nullable=False, default=list)
    is_new = Column(Boolean, nullable=False, default=False)
    position = Column(Integer, nullable=False, default=0)
    extra_fields = Column(JSON, nullable=True)


class ContentArtistAlbumTrack(Base):
    """Track reference inside an artist album."""
    __tablename__ = 'content_artist_album_tracks'

    id = Column(Integer, primary_key=True)
    album_id_ref = Column(String(100), nullable=False, index=True)
    track_id_ref = Column(String(50), nullable=False, default='')
    title = Column(String(500), nullable=False, default='')
    position = Column(Integer, nullable=False, default=0)


class ContentArtistShow(Base):
    """Show reference nested inside an artist record."""
    __tablename__ = 'content_artist_shows'

    id = Column(Integer, primary_key=True)
    artist_id_ref = Column(String(50), nullable=False, index=True)
    show_ref_id = Column(String(100), nullable=False, default='')
    title = Column(String(500), nullable=False, default='')
    show_type = Column(String(50), nullable=False, default='')
    duration = Column(Integer, nullable=False, default=0)
    category = Column(String(100), nullable=False, default='')
    published_date = Column(String(50), nullable=False, default='')
    position = Column(Integer, nullable=False, default=0)


class ContentArtistTrack(Base):
    """Track reference nested inside an artist record."""
    __tablename__ = 'content_artist_tracks'

    id = Column(Integer, primary_key=True)
    artist_id_ref = Column(String(50), nullable=False, index=True)
    track_ref_id = Column(String(50), nullable=False, default='')
    title = Column(String(500), nullable=False, default='')
    album = Column(String(255), nullable=False, default='')
    duration = Column(Integer, nullable=False, default=0)
    genre = Column(String(100), nullable=False, default='')
    added_date = Column(String(50), nullable=False, default='')
    position = Column(Integer, nullable=False, default=0)


class PodcastShow(Base):
    """Podcast series — source of truth for /api/podcasts."""
    __tablename__ = 'content_podcast_shows'

    id = Column(Integer, primary_key=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, default='')
    description = Column(String(5000), nullable=False, default='')
    artwork = Column(String(1024), nullable=False, default='')
    last_updated = Column(String(50), nullable=False, default='')
    position = Column(Integer, nullable=False, default=0)


class PodcastEpisode(Base):
    """Podcast episode within a show."""
    __tablename__ = 'content_podcast_episodes'

    id = Column(Integer, primary_key=True)
    episode_id = Column(String(100), unique=True, nullable=False, index=True)
    show_slug = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False, default='')
    description = Column(String(5000), nullable=False, default='')
    date = Column(String(50), nullable=False, default='')
    duration = Column(String(50), nullable=False, default='')  # "18:42"
    duration_seconds = Column(Integer, nullable=False, default=0)
    audio_url = Column(String(1024), nullable=False, default='')
    artwork = Column(String(1024), nullable=False, default='')
    position = Column(Integer, nullable=False, default=0)


class Event(Base):
    """Event — source of truth for /events (was events.json)."""
    __tablename__ = 'content_events'

    id = Column(Integer, primary_key=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False, default='')
    date = Column(String(50), nullable=False, default='')
    time = Column(String(100), nullable=False, default='')
    venue = Column(String(255), nullable=False, default='')
    venue_address = Column(String(500), nullable=False, default='')
    event_type = Column(String(50), nullable=False, default='')
    status = Column(String(50), nullable=False, default='upcoming')
    description = Column(String(5000), nullable=False, default='')
    photos = Column(JSON, nullable=False, default=list)
    image = Column(String(1024), nullable=False, default='')
    rsvp_external_url = Column(String(1024), nullable=True)
    rsvp_enabled = Column(Boolean, nullable=False, default=True)
    rsvp_limit = Column(String(50), nullable=True)
    position = Column(Integer, nullable=False, default=0, index=True)
    extra_fields = Column(JSON, nullable=True)


class ContentMerch(Base):
    """Merch item — source of truth for merch catalog (was data/merch.json)."""
    __tablename__ = 'content_merch'

    id = Column(Integer, primary_key=True)
    item_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False, default='')
    image_url = Column(String(1024), nullable=False, default='')
    image_url_back = Column(String(1024), nullable=True)
    price_usd = Column(Float, nullable=False, default=20.0)
    kind = Column(String(50), nullable=False, default='merch')
    available = Column(Boolean, nullable=False, default=True)
    position = Column(Integer, nullable=False, default=0, index=True)
    extra_fields = Column(JSON, nullable=True)

