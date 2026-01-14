/**
 * Now Playing Component - Main controller for the glassy Now Playing bar
 * Integrates color extraction for the glassy theme.
 *
 * NOTE: Visualizer is removed. Keep this controller light and avoid WebAudio init.
 */

class NowPlayingController {
    constructor() {
        this.visualizer = null;
        this.currentColors = null;
        this.isInitialized = false;
        this.audioElement = null;
        this.animationFrame = null;
        this.lastTrackId = null;
    }

    /**
     * Initialize the Now Playing component
     */
    async init() {
        if (this.isInitialized) return;

        try {
            // Setup visualizer container
            // Visualizer removed (Three.js). Keep container empty.
            this.visualizer = null;

            // Listen for track changes
            this.setupTrackListeners();

            this.isInitialized = true;
        } catch (error) {
            console.error('Error initializing NowPlayingController:', error);
        }
    }

    /**
     * Setup listeners for track changes
     */
    setupTrackListeners() {
        // Listen to mediaPlayer events
        if (window.mediaPlayer) {
            window.mediaPlayer.on('play', () => {
                const track = window.mediaPlayer.currentTrack;
                if (track) {
                    this.onTrackChange(track);
                }
            });
        }

        // Listen for Alpine.js updates (if using Alpine)
        document.addEventListener('trackchange', (e) => {
            if (e.detail && e.detail.track) {
                this.onTrackChange(e.detail.track);
            }
        });

        // Listen for play-track events
        document.addEventListener('play-track', (e) => {
            const track = e.detail && (e.detail.track || e.detail);
            if (track) {
                setTimeout(() => {
                    this.onTrackChange(track);
                }, 100);
            }
        });
    }

    /**
     * Handle track change
     */
    async onTrackChange(track) {
        if (!track) return;

        // Extract colors from album art
        const coverArt = track.cover_art || track.cover || '/static/img/default-cover.jpg';
        if (window.colorExtractor && typeof window.colorExtractor.extractColors === 'function') {
            this.currentColors = await window.colorExtractor.extractColors(coverArt);
        } else {
            this.currentColors = { dominant: '#6366f1', secondary: '#8b5cf6', accent: '#ec4899' };
        }

        // Update CSS variables for glass effect
        this.updateGlassColors(this.currentColors);

        // Update album artwork glow
        this.updateAlbumGlow(this.currentColors.dominant);

        // Visualizer removed: no audio analysis work needed here.
    }

    /**
     * Update glass effect colors via CSS variables
     */
    updateGlassColors(colors) {
        const nowPlayingBar = document.querySelector('.now-playing-glass');
        if (!nowPlayingBar) return;

        // Convert hex to rgba for gradient
        const dominantRgb = this.hexToRgb(colors.dominant);
        const secondaryRgb = this.hexToRgb(colors.secondary);

        if (dominantRgb && secondaryRgb) {
            const gradient = `linear-gradient(135deg, 
                rgba(${dominantRgb.r}, ${dominantRgb.g}, ${dominantRgb.b}, 0.15) 0%,
                rgba(${secondaryRgb.r}, ${secondaryRgb.g}, ${secondaryRgb.b}, 0.1) 100%)`;

            nowPlayingBar.style.setProperty('--glass-gradient', gradient);
            nowPlayingBar.style.setProperty('--dominant-color', colors.dominant);
            nowPlayingBar.style.setProperty('--secondary-color', colors.secondary);
            nowPlayingBar.style.setProperty('--accent-color', colors.accent);
        }
    }

    /**
     * Update album artwork glow
     */
    updateAlbumGlow(color) {
        const albumArt = document.querySelector('.now-playing-album-art img');
        if (albumArt) {
            const rgb = this.hexToRgb(color);
            if (rgb) {
                albumArt.style.boxShadow = `0 0 20px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.5)`;
            }
        }
    }

    /**
     * Start update loop for visualizer
     */
    startUpdateLoop() {
        // Visualizer removed: no-op.
        if (!this.visualizer) return;
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }

        const update = () => {
            this.animationFrame = requestAnimationFrame(update);
        };

        update();
    }

    /**
     * Stop update loop
     */
    stopUpdateLoop() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
            this.animationFrame = null;
        }
    }

    /**
     * Hex to RGB helper
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stopUpdateLoop();
        
        if (this.visualizer) {
            this.visualizer.destroy();
            this.visualizer = null;
        }

        this.isInitialized = false;
    }
}

// Export singleton instance
window.nowPlayingController = new NowPlayingController();

// Lazy initialize to keep mobile load fast:
// - Initialize when the user starts playback (best signal we actually need the glass theme).
// - Also initialize on first interaction as a fallback.
(function lazyInitNowPlaying() {
    let started = false;
    const start = () => {
        if (started) return;
        started = true;
        try { window.nowPlayingController.init(); } catch (_) {}
        document.removeEventListener('play-track', start);
        document.removeEventListener('click', start, true);
        document.removeEventListener('touchstart', start, true);
    };
    document.addEventListener('play-track', start, { once: true });
    document.addEventListener('click', start, { once: true, capture: true });
    document.addEventListener('touchstart', start, { once: true, capture: true });
})();

