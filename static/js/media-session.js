/**
 * Media Session API integration for Ahoy Indie Media
 * Provides background audio controls and metadata display
 */

class MediaSessionManager {
    constructor() {
        this.isSupported = 'mediaSession' in navigator;
        this.currentTrack = null;
        this.player = null;
    }

    /**
     * Initialize media session with player controls
     * @param {Object} player - Audio player instance with play/pause/seek methods
     */
    init(player) {
        if (!this.isSupported) {
            console.log('Media Session API not supported');
            return;
        }

        this.player = player;
        this.setupActionHandlers();
    }

    /**
     * Set up media session action handlers
     */
    setupActionHandlers() {
        if (!this.isSupported || !this.player) return;

        navigator.mediaSession.setActionHandler('play', () => {
            console.log('Media session: play');
            this.player.play();
        });

        navigator.mediaSession.setActionHandler('pause', () => {
            console.log('Media session: pause');
            this.player.pause();
        });

        navigator.mediaSession.setActionHandler('previoustrack', () => {
            console.log('Media session: previous track');
            if (this.player.prev) this.player.prev();
        });

        navigator.mediaSession.setActionHandler('nexttrack', () => {
            console.log('Media session: next track');
            if (this.player.next) this.player.next();
        });

        navigator.mediaSession.setActionHandler('seekto', (details) => {
            console.log('Media session: seek to', details.seekTime);
            if (this.player.seek) this.player.seek(details.seekTime);
        });

        navigator.mediaSession.setActionHandler('seekbackward', (details) => {
            console.log('Media session: seek backward', details.seekOffset);
            if (this.player.seekBackward) this.player.seekBackward(details.seekOffset);
        });

        navigator.mediaSession.setActionHandler('seekforward', (details) => {
            console.log('Media session: seek forward', details.seekOffset);
            if (this.player.seekForward) this.player.seekForward(details.seekOffset);
        });
    }

    /**
     * Update media session metadata
     * @param {Object} track - Track information
     */
    updateMetadata(track) {
        if (!this.isSupported) return;

        this.currentTrack = track;

        const metadata = new MediaMetadata({
            title: track.title || 'Unknown Title',
            artist: track.artist || 'Unknown Artist',
            album: track.album || 'Ahoy Indie Media',
            artwork: [
                {
                    src: track.cover_art || track.thumbnail || '/static/images/default-cover.png',
                    sizes: '512x512',
                    type: 'image/png'
                }
            ]
        });

        navigator.mediaSession.metadata = metadata;
        console.log('Media session metadata updated:', track.title);
    }

    /**
     * Update playback state
     * @param {string} state - 'playing', 'paused', or 'none'
     */
    updatePlaybackState(state) {
        if (!this.isSupported) return;

        navigator.mediaSession.playbackState = state;
        console.log('Media session playback state:', state);
    }

    /**
     * Set position state for seeking
     * @param {Object} positionState - Position information
     */
    setPositionState(positionState) {
        if (!this.isSupported) return;

        navigator.mediaSession.setPositionState(positionState);
    }
}

// Global instance
window.mediaSessionManager = new MediaSessionManager();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MediaSessionManager;
}
