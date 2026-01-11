/**
 * Now Playing Component - Main controller for the glassy Now Playing bar
 * Integrates color extraction, audio analysis, and visualizer
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
            // Wait for Three.js to load
            if (!window.THREE) {
                console.warn('Three.js not loaded yet, waiting...');
                await this.waitForThree();
            }

            // Setup visualizer container
            const visualizerContainer = document.getElementById('now-playing-visualizer');
            if (visualizerContainer) {
                this.visualizer = new Visualizer(visualizerContainer, {
                    type: 'bars',
                    maxFPS: 45
                });
                
                if (this.visualizer.init()) {
                    // Do not start the render loop until playback begins.
                    // This saves CPU/GPU on mobile when nothing is playing.
                }
            }

            // Setup audio element connection
            this.setupAudioConnection();

            // Listen for track changes
            this.setupTrackListeners();

            this.isInitialized = true;
        } catch (error) {
            console.error('Error initializing NowPlayingController:', error);
        }
    }

    /**
     * Wait for Three.js to be loaded
     */
    waitForThree() {
        return new Promise((resolve) => {
            if (window.THREE) {
                resolve();
                return;
            }

            const checkInterval = setInterval(() => {
                if (window.THREE) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);

            // Timeout after 5 seconds
            setTimeout(() => {
                clearInterval(checkInterval);
                resolve();
            }, 5000);
        });
    }

    /**
     * Setup audio element connection
     */
    setupAudioConnection() {
        // Find audio element from mediaPlayer
        if (window.mediaPlayer && window.mediaPlayer.audioElement) {
            this.audioElement = window.mediaPlayer.audioElement;
            this.connectAudio();
        }

        // Listen for audio element creation
        const checkAudio = setInterval(() => {
            if (window.mediaPlayer && window.mediaPlayer.audioElement && !this.audioElement) {
                this.audioElement = window.mediaPlayer.audioElement;
                this.connectAudio();
                clearInterval(checkAudio);
            }
        }, 500);

        // Stop checking after 5 seconds (keep it light)
        setTimeout(() => clearInterval(checkAudio), 5000);

        // Initialize audio context on first user interaction (browser security requirement)
        const initOnInteraction = async () => {
            if (window.audioAnalyser && !window.audioAnalyser.isInitialized) {
                const initialized = await window.audioAnalyser.initialize();
                if (initialized && this.audioElement) {
                    this.connectAudio();
                }
            }
            // Remove listeners after first interaction
            document.removeEventListener('click', initOnInteraction);
            document.removeEventListener('touchstart', initOnInteraction);
        };

        document.addEventListener('click', initOnInteraction, { once: true });
        document.addEventListener('touchstart', initOnInteraction, { once: true });
    }

    /**
     * Connect audio element to analyser
     */
    connectAudio() {
        if (!this.audioElement) return;

        // Don't connect if audio is already playing - wait for next track change
        // This prevents breaking existing audio connections
        if (this.audioElement.src && !this.audioElement.paused) {
            // Audio is already playing, try to connect but don't break if it fails
            if (window.audioAnalyser.isInitialized) {
                const connected = window.audioAnalyser.connect(this.audioElement);
                if (connected) {
                    // Update loop + visualizer render start on playback events.
                    window.audioAnalyser.resume();
                }
            }
            return;
        }

        // Ensure audio context is initialized
        if (!window.audioAnalyser.isInitialized) {
            window.audioAnalyser.initialize().then((initialized) => {
                if (initialized) {
                    // Try to connect, but don't break playback if it fails
                    const connected = window.audioAnalyser.connect(this.audioElement);
                    if (connected) {
                        window.audioAnalyser.resume();
                    }
                }
            });
        } else {
            // Try to connect, but don't break playback if it fails
            const connected = window.audioAnalyser.connect(this.audioElement);
            if (connected) {
                window.audioAnalyser.resume();
            }
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
                // Start loops only while playing (CPU/GPU win on mobile).
                try { this.visualizer && this.visualizer.start(); } catch (_) {}
                try { this.startUpdateLoop(); } catch (_) {}
            });
            window.mediaPlayer.on('pause', () => {
                try { this.stopUpdateLoop(); } catch (_) {}
                try { this.visualizer && this.visualizer.stop(); } catch (_) {}
            });
            window.mediaPlayer.on('ended', () => {
                try { this.stopUpdateLoop(); } catch (_) {}
                try { this.visualizer && this.visualizer.stop(); } catch (_) {}
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
        this.currentColors = await window.colorExtractor.extractColors(coverArt);

        // Update visualizer colors
        if (this.visualizer) {
            this.visualizer.updateColors(this.currentColors);
        }

        // Update CSS variables for glass effect
        this.updateGlassColors(this.currentColors);

        // Update album artwork glow
        this.updateAlbumGlow(this.currentColors.dominant);

        // Don't try to reconnect audio here - let player.js handle it after playback starts
        // This prevents breaking the audio connection
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
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }

        const update = () => {
            if (window.audioAnalyser && window.audioAnalyser.isInitialized) {
                const frequencyData = window.audioAnalyser.getFrequencyData();
                if (frequencyData && this.visualizer) {
                    this.visualizer.update(frequencyData);
                }
            }

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

        if (window.audioAnalyser) {
            window.audioAnalyser.disconnect();
        }

        this.isInitialized = false;
    }
}

// Export singleton instance
window.nowPlayingController = new NowPlayingController();

// Lazy initialize to keep mobile load fast:
// - Initialize when the user starts playback (best signal we actually need the visualizer/analyser).
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

