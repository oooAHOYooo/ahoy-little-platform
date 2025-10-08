from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    playlists = relationship('Playlist', back_populates='user', cascade='all, delete-orphan')
    bookmarks = relationship('Bookmark', back_populates='user', cascade='all, delete-orphan')
    play_history = relationship('PlayHistory', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


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


