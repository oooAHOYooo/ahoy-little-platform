/**
 * Now Playing - Glass theme color controller
 * Extracts colors from album art for the glassy Now Playing bar styling.
 */

class NowPlayingController {
    constructor() {
        this.currentColors = null;
        this.isInitialized = false;
    }

    init() {
        if (this.isInitialized) return;
        this.setupTrackListeners();
        this.isInitialized = true;
    }

    setupTrackListeners() {
        if (window.mediaPlayer) {
            window.mediaPlayer.on('play', () => {
                const track = window.mediaPlayer.currentTrack;
                if (track) this.onTrackChange(track);
            });
        }

        document.addEventListener('trackchange', (e) => {
            if (e.detail?.track) this.onTrackChange(e.detail.track);
        });

        document.addEventListener('play-track', (e) => {
            const track = e.detail?.track || e.detail;
            if (track) setTimeout(() => this.onTrackChange(track), 100);
        });
    }

    async onTrackChange(track) {
        if (!track) return;

        const coverArt = track.cover_art || track.cover || '/static/img/default-cover.jpg';

        try {
            if (window.colorExtractor?.extractColors) {
                this.currentColors = await window.colorExtractor.extractColors(coverArt);
            } else {
                this.currentColors = { dominant: '#6366f1', secondary: '#8b5cf6', accent: '#ec4899' };
            }
        } catch (e) {
            this.currentColors = { dominant: '#6366f1', secondary: '#8b5cf6', accent: '#ec4899' };
        }

        this.updateGlassColors(this.currentColors);
        this.updateAlbumGlow(this.currentColors.dominant);
    }

    updateGlassColors(colors) {
        const nowPlayingBar = document.querySelector('.now-playing-glass');
        if (!nowPlayingBar) return;

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

    updateAlbumGlow(color) {
        const albumArt = document.querySelector('.now-playing-album-art img');
        if (albumArt) {
            const rgb = this.hexToRgb(color);
            if (rgb) {
                albumArt.style.boxShadow = `0 0 20px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.5)`;
            }
        }
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }
}

// Singleton
window.nowPlayingController = new NowPlayingController();

// Lazy init on first interaction
(function() {
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
    document.addEventListener('touchstart', start, { once: true, capture: true, passive: true });
})();
