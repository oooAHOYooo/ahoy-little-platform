"""
ARCHIVED: Shadowed Blueprint Files
===================================

This file contains the shadowed blueprint code that was removed from the main codebase.
These blueprints were registered but never reached because API blueprints with the same
URL prefix were registered first and shadowed them.

Date Archived: December 2024
Reason: Blueprints were shadowed by API blueprints, never executed, causing confusion.

If you need to restore this functionality:
1. These were file-based implementations (JSON storage)
2. Current system uses database-based API blueprints in blueprints/api/
3. Use blueprints/api/playlists.py and blueprints/api/bookmarks.py instead
"""

# ============================================================================
# ARCHIVED: blueprints/playlists.py
# ============================================================================
# This blueprint was shadowed by blueprints/api/playlists.py
# Both used the same URL prefix "/api/playlists"
# The API blueprint was registered first, so this one was never reached

# See original file content in git history if needed

# ============================================================================
# ARCHIVED: blueprints/bookmarks.py  
# ============================================================================
# This blueprint was shadowed by blueprints/api/bookmarks.py
# Both used the same URL prefix "/api/bookmarks"
# The API blueprint was registered first, so this one was never reached

# See original file content in git history if needed

# ============================================================================
# NOTES
# ============================================================================

"""
These blueprints used file-based JSON storage (data/playlists.json, data/bookmarks.json)
The current system uses database-based storage via SQLAlchemy models.

The shadowed blueprints were:
- blueprints/playlists.py - File-based playlist management
- blueprints/bookmarks.py - File-based bookmark management

Both were registered in app.py but never executed because:
1. blueprints/api/playlists.py was registered first (line ~164)
2. blueprints/api/bookmarks.py was registered first (line ~165)
3. Flask uses first-match routing, so shadowed blueprints never received requests

Removing these eliminates confusion and dead code.
"""

