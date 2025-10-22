#!/usr/bin/env python3
"""
Password security utilities for Ahoy Indie Media
Consolidated bcrypt-based password hashing with legacy SHA-256 support
"""

import hashlib
import structlog
import bcrypt

logger = structlog.get_logger()

# Legacy salt for SHA-256 hashes
LEGACY_SALT = "ahoy_indie_media_2025"


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash (supports both bcrypt and legacy SHA-256)"""
    if not password or not hashed:
        return False
    
    # Check if it's a bcrypt hash (starts with $2b$)
    if hashed.startswith('$2b$'):
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            logger.error("bcrypt verification failed", error=str(e))
            return False
    
    # Legacy SHA-256 verification
    if len(hashed) == 64:  # SHA-256 hex length
        legacy_hash = hashlib.sha256((password + LEGACY_SALT).encode()).hexdigest()
        return legacy_hash == hashed
    
    # Unknown hash format
    logger.warning("Unknown password hash format", hash_length=len(hashed))
    return False


def rehash_legacy_password(password: str, old_hash: str, user_id: str = None) -> str:
    """Rehash a legacy SHA-256 password to bcrypt"""
    # Verify the old hash first
    if not verify_password(password, old_hash):
        raise ValueError("Invalid password for legacy hash")
    
    # Generate new bcrypt hash
    new_hash = hash_password(password)
    
    # Log the rehash operation
    logger.info("password_rehash",
               scheme_from="sha256",
               scheme_to="bcrypt",
               user_id=user_id)
    
    return new_hash


def is_legacy_hash(hashed: str) -> bool:
    """Check if a hash is legacy SHA-256 format"""
    return len(hashed) == 64 and not hashed.startswith('$2b$')
