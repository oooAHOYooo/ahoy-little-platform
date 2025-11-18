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

            // Initialize audio analyser
            const audioInit = await window.audioAnalyser.initialize();
            if (!audioInit) {
                console.warn('Audio analyser initialization failed');
            }

            // Setup visualizer container
            const visualizerContainer = document.getElementById('now-playing-visualizer');
            if (visualizerContainer) {
                this.visualizer = new Visualizer(visualizerContainer, {
                    type: 'bars',
                    maxFPS: 45
                });
                
                if (this.visualizer.init()) {
                    this.visualizer.start();
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

        // Stop checking after 10 seconds
        setTimeout(() => clearInterval(checkAudio), 10000);

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
                    this.startUpdateLoop();
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
                        this.startUpdateLoop();
                        window.audioAnalyser.resume();
                    }
                }
            });
        } else {
            // Try to connect, but don't break playback if it fails
            const connected = window.audioAnalyser.connect(this.audioElement);
            if (connected) {
                this.startUpdateLoop();
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

        // Poll for track changes (fallback)
        setInterval(() => {
            if (window.mediaPlayer && window.mediaPlayer.currentTrack) {
                const currentTrack = window.mediaPlayer.currentTrack;
                // Only update if track actually changed
                if (!this.lastTrackId || this.lastTrackId !== currentTrack.id) {
                    this.lastTrackId = currentTrack.id;
                    this.onTrackChange(currentTrack);
                }
            }
        }, 1000);
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

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.nowPlayingController.init();
    });
} else {
    window.nowPlayingController.init();
}

