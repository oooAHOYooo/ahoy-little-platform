// Ahoy Indie Media - Player JavaScript

// Player state management
class MediaPlayer {
    constructor() {
        this.currentTrack = null;
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 0;
        this.volume = 1;
        this.isMuted = false;
        this.isShuffled = false;
        this.isRepeated = false;
        this.playlist = [];
        this.currentIndex = 0;
        this.audioElement = null;
        this.videoElement = null;
        this.eventListeners = new Map();
        // Passive listening-time tracker (persisted)
        this.listening = {
            totalSec: parseInt(localStorage.getItem('ahoy.listening.totalSec') || '0', 10) || 0,
            lastTick: null,
            lastPersist: 0
        };

        this.initializePlayer();
        this._restoreState();
    }
    
    initializePlayer() {
        // Create audio element for music
        this.audioElement = document.createElement('audio');
        this.audioElement.preload = 'auto'; // Use 'auto' for faster loading
        // Improve compatibility with iOS/Safari
        try { this.audioElement.setAttribute('playsinline', ''); } catch (_) {}
        // Note: crossOrigin removed - causes CORS issues with S3 and visualizer is disabled
        this.audioElement.style.display = 'none';
        document.body.appendChild(this.audioElement);

        // Create video element for shows
        this.videoElement = document.createElement('video');
        this.videoElement.preload = 'auto'; // Use 'auto' for faster loading
        try { this.videoElement.setAttribute('playsinline', ''); } catch (_) {}
        this.videoElement.style.display = 'none';
        document.body.appendChild(this.videoElement);

        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Audio events
        this.audioElement.addEventListener('loadstart', () => {
            this.emit('loading', true);
        });
        this.audioElement.addEventListener('loadedmetadata', () => {
            this.duration = this.audioElement.duration;
            this.emit('durationchange', this.duration);
        });
        this.audioElement.addEventListener('canplay', () => {
            this.emit('loading', false);
        });
        this.audioElement.addEventListener('canplaythrough', () => {
            this.emit('loading', false);
            this.emit('canplaythrough');
        });
        this.audioElement.addEventListener('waiting', () => {
            this.emit('loading', true);
            this.emit('buffering', true);
        });
        this.audioElement.addEventListener('playing', () => {
            this.emit('loading', false);
            this.emit('buffering', false);
        });
        this.audioElement.addEventListener('error', () => {
            this.emit('loading', false);
            try {
                const code = (this.audioElement.error && this.audioElement.error.code) || 'unknown';
                console.error('Audio element error, code:', code, this.audioElement.error);
                document.dispatchEvent(new CustomEvent('ahoy:toast', { detail: 'Audio failed to load. Trying again…' }));
            } catch (_) {}
            // Try fallbacks: if we have alternative sources for the current track, rotate to the next one
            try {
                if (this._fallbackSources && Array.isArray(this._fallbackSources) && this._fallbackIndex != null) {
                    const nextIdx = this._fallbackIndex + 1;
                    if (nextIdx < this._fallbackSources.length) {
                        this._fallbackIndex = nextIdx;
                        const nextSrc = this._fallbackSources[this._fallbackIndex];
                        if (typeof nextSrc === 'string' && nextSrc.trim()) {
                            // Bust cache slightly to avoid stale errors
                            const srcWithBuster = nextSrc + (nextSrc.includes('?') ? '&' : '?') + 'v=' + Date.now();
                            this.audioElement.src = srcWithBuster;
                            try { this.audioElement.load(); } catch (_) {}
                            this.audioElement.play().catch(() => {/* ignore; policy-locked will retry on gesture */});
                            return;
                        }
                    }
                }
            } catch (e) {
                console.warn('Fallback rotation failed:', e);
            }
            // Last fallback: if crossOrigin is set, clear it and retry once (disables analyser but may allow playback)
            try {
                if (!this._clearedCorsOnce) {
                    this._clearedCorsOnce = true;
                    try { this.audioElement.removeAttribute('crossorigin'); } catch (_) {}
                    const cur = this.audioElement.currentSrc || this.audioElement.src;
                    if (cur) {
                        // reload same URL (no extra cache buster to avoid 403 loops)
                        this.audioElement.src = cur;
                        try { this.audioElement.load(); } catch (_) {}
                        this.audioElement.play().catch(() => {});
                        return;
                    }
                }
            } catch (_) {}
            // Final soft retry by reloading the current source once
            try { this.audioElement.load(); } catch (_) {}
        });
        // Network hiccup handling - attempt a single gentle retry
        ['stalled','suspend','abort'].forEach(evt => {
            this.audioElement.addEventListener(evt, () => {
                if (!this._networkRetried && this.currentTrack) {
                    this._networkRetried = true;
                    try { this.audioElement.load(); } catch (_) {}
                    this.audioElement.play().catch(()=>{});
                    setTimeout(() => { this._networkRetried = false; }, 5000);
                }
            });
        });
        
        this.audioElement.addEventListener('timeupdate', () => {
            this.currentTime = this.audioElement.currentTime;
            this.emit('timeupdate', this.currentTime);
            this._onTimeProgress();
        });
        
        this.audioElement.addEventListener('play', () => {
            this.isPlaying = true;
            this.emit('play');
            this._onStarted();
        });
        
        this.audioElement.addEventListener('pause', () => {
            this.isPlaying = false;
            this.emit('pause');
            this._onPaused();
        });
        
        this.audioElement.addEventListener('ended', () => {
            this.isPlaying = false;
            this.emit('ended');
            this.handleTrackEnd();
            this._onPaused();
        });
        
        this.audioElement.addEventListener('volumechange', () => {
            this.volume = this.audioElement.volume;
            this.isMuted = this.audioElement.muted;
            this.emit('volumechange', { volume: this.volume, muted: this.isMuted });
        });
        
        // Video events
        this.videoElement.addEventListener('loadstart', () => {
            this.emit('loading', true);
        });
        this.videoElement.addEventListener('loadedmetadata', () => {
            this.duration = this.videoElement.duration;
            this.emit('durationchange', this.duration);
        });
        this.videoElement.addEventListener('canplay', () => {
            this.emit('loading', false);
        });
        this.videoElement.addEventListener('canplaythrough', () => {
            this.emit('loading', false);
        });
        this.videoElement.addEventListener('waiting', () => {
            this.emit('loading', true);
            this.emit('buffering', true);
        });
        this.videoElement.addEventListener('playing', () => {
            this.emit('loading', false);
            this.emit('buffering', false);
        });
        this.videoElement.addEventListener('error', () => {
            this.emit('loading', false);
            console.error('Video element error:', this.videoElement.error);
        });
        
        this.videoElement.addEventListener('timeupdate', () => {
            this.currentTime = this.videoElement.currentTime;
            this.emit('timeupdate', this.currentTime);
            this._onTimeProgress();
        });
        
        this.videoElement.addEventListener('play', () => {
            this.isPlaying = true;
            this.emit('play');
            this._onStarted();
        });
        
        this.videoElement.addEventListener('pause', () => {
            this.isPlaying = false;
            this.emit('pause');
            this._onPaused();
        });
        
        this.videoElement.addEventListener('ended', () => {
            this.isPlaying = false;
            this.emit('ended');
            this.handleTrackEnd();
            this._onPaused();
        });
        
        this.videoElement.addEventListener('volumechange', () => {
            this.volume = this.videoElement.volume;
            this.isMuted = this.videoElement.muted;
            this.emit('volumechange', { volume: this.volume, muted: this.isMuted });
        });
    }
    
    // Event system
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
    
    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                callback(data);
            });
        }
    }
    
    // Player controls
    play(track) {
        const previousTrack = this.currentTrack;
        
        // If same track is already playing, just resume if paused
        if (previousTrack && previousTrack.id === track.id && previousTrack.title === track.title) {
            const isVideo = track.type === 'show' || track.video_url || track.mp4_link;
            const mediaElement = isVideo ? this.videoElement : this.audioElement;
            
            if (mediaElement.paused) {
                const playFn = mediaElement.play && mediaElement.play.bind(mediaElement);
                if (playFn) {
                    playFn().then(() => {
                        this.isPlaying = true;
                        this.emit('play');
                    }).catch(error => {
                        if (error && error.name === 'AbortError') return;
                        console.error('Error resuming media:', error);
                        this.emit('error', error);
                    });
                }
            }
            return;
        }
        
        this.currentTrack = track;
        
        // Emit trackchange event if track actually changed
        if (previousTrack !== track && (previousTrack?.id !== track?.id || previousTrack?.title !== track?.title)) {
            this.emit('trackchange', track);
            // Track recently played for habit discovery
            if (window.trackRecentPlay) {
                window.trackRecentPlay(track);
            }
        }
        
        // Determine which element to use
        const isVideo = track.type === 'show' || track.video_url || track.mp4_link;
        const mediaElement = isVideo ? this.videoElement : this.audioElement;
        
        // Pause other element first
        if (isVideo) {
            if (!this.audioElement.paused) {
                this.audioElement.pause();
            }
        } else {
            if (!this.videoElement.paused) {
                this.videoElement.pause();
            }
        }
        
        // Set source - try multiple possible URL fields and prepare fallback list
        let source = null;
        if (isVideo) {
            const candidates = [track.video_url, track.mp4_link, track.url].filter(Boolean);
            this._fallbackSources = candidates;
            this._fallbackIndex = 0;
            source = candidates[0] || null;
        } else {
            // Prioritize full tracks over previews - if full_url exists, use it instead of preview_url
            // This prevents 30-second previews from playing when full tracks are available
            const candidates = [];
            if (track.audio_url) candidates.push(track.audio_url);
            if (track.full_url) candidates.push(track.full_url); // Prefer full_url over preview_url
            if (track.preview_url && !track.full_url) candidates.push(track.preview_url); // Only use preview if no full_url
            if (track.url) candidates.push(track.url);
            if (track.src) candidates.push(track.src);
            
            this._fallbackSources = candidates;
            this._fallbackIndex = 0;
            source = candidates[0] || null;
        }
        
        if (!source) {
            console.error('No audio/video source available for track:', track);
            this.emit('error', new Error('No source available'));
            return;
        }
        
        // Always set source and play - browser handles same-source efficiently
        if (typeof source === 'string' && source.trim()) {
            // Abort any pending play promise to prevent AbortError
            this._playAborted = true;

            // Pause current playback before changing source
            if (!mediaElement.paused) {
                mediaElement.pause();
            }

            // Emit loading event for UI feedback
            this.emit('loading', true);

            // Use source URL directly - no cache buster to enable browser caching
            mediaElement.src = source;
            mediaElement.volume = this.volume;
            mediaElement.muted = this.isMuted;

            // Load the new source (required by some browsers before play)
            try { mediaElement.load(); } catch (e) { /* ignore */ }

            // Reset abort flag and play immediately - browser will buffer and start as soon as data arrives
            this._playAborted = false;
            const playFn = mediaElement.play && mediaElement.play.bind(mediaElement);
            const playPromise = playFn ? playFn() : undefined;

            if (playPromise !== undefined) {
                playPromise.then(() => {
                    // Check if this play was aborted by a newer track
                    if (this._playAborted) return;

                    this.isPlaying = true;
                    this.emit('loading', false);
                    this.emit('play');

                    // Update Now Playing glass theme colors
                    if (!isVideo && window.nowPlayingController) {
                        window.nowPlayingController.onTrackChange(track);
                    }
                }).catch(error => {
                    // Clear loading state on error
                    this.emit('loading', false);
                    // Ignore if aborted by a newer track selection
                    if (this._playAborted) return;

                    // AbortError is expected when switching tracks quickly - ignore silently
                    if (error.name === 'AbortError') return;

                    // NotAllowedError: autoplay policy - wait for user gesture
                    if (typeof error?.name === 'string' && error.name.toLowerCase().includes('notallowed')) {
                        const retryOnGesture = () => {
                            if (this._playAborted) return;
                            const playAgain = mediaElement.play && mediaElement.play.bind(mediaElement);
                            if (playAgain) playAgain().then(() => {
                                if (this._playAborted) return;
                                this.isPlaying = true;
                                this.emit('play');
                                document.removeEventListener('click', retryOnGesture, { capture: true });
                                document.removeEventListener('touchstart', retryOnGesture, { capture: true });
                            }).catch(() => {});
                        };
                        document.addEventListener('click', retryOnGesture, { once: true, capture: true });
                        document.addEventListener('touchstart', retryOnGesture, { once: true, capture: true, passive: true });
                        try { document.dispatchEvent(new CustomEvent('ahoy:toast', { detail: 'Tap anywhere to start audio' })); } catch (_) {}
                    } else {
                        console.error('Error playing media:', error);
                        this.emit('error', error);
                    }
                });
            }
        }
    }
    
    pause() {
        this.isPlaying = false;
        if (this.audioElement && !this.audioElement.paused) {
            this.audioElement.pause();
        }
        if (this.videoElement && !this.videoElement.paused) {
            this.videoElement.pause();
        }
    }
    
    resume() {
        const activeElement = this.getActiveElement();
        if (activeElement && activeElement.play) {
            const playFn = activeElement.play.bind(activeElement);
            playFn().catch(error => {
                if (error && error.name === 'AbortError') return;
                console.error('Error resuming media:', error);
                this.emit('error', error);
            });
        }
    }
    
    stop() {
        this.pause();
        this.currentTime = 0;
        this.currentTrack = null;
        this.audioElement.currentTime = 0;
        this.videoElement.currentTime = 0;
        this.emit('stop');
    }
    
    seekTo(time) {
        const activeElement = this.getActiveElement();
        if (activeElement) {
            activeElement.currentTime = time;
            this.currentTime = time;
        }
    }
    
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        this.audioElement.volume = this.volume;
        this.videoElement.volume = this.volume;
        this.emit('volumechange', { volume: this.volume, muted: this.isMuted });
    }
    
    setMuted(muted) {
        this.isMuted = muted;
        this.audioElement.muted = muted;
        this.videoElement.muted = muted;
        this.emit('volumechange', { volume: this.volume, muted: this.isMuted });
    }
    
    toggleMute() {
        this.setMuted(!this.isMuted);
    }
    
    // Playlist management
    setPlaylist(playlist) {
        this.playlist = playlist;
        this.currentIndex = 0;
        this.emit('playlistchange', this.playlist);
    }
    
    addToPlaylist(track) {
        this.playlist.push(track);
        this.emit('playlistchange', this.playlist);
    }
    
    removeFromPlaylist(index) {
        if (index >= 0 && index < this.playlist.length) {
            this.playlist.splice(index, 1);
            if (index < this.currentIndex) {
                this.currentIndex--;
            } else if (index === this.currentIndex && this.currentIndex >= this.playlist.length) {
                this.currentIndex = Math.max(0, this.playlist.length - 1);
            }
            this.emit('playlistchange', this.playlist);
        }
    }
    
    nextTrack() {
        if (this.playlist.length === 0) return;
        
        if (this.isShuffled) {
            this.currentIndex = Math.floor(Math.random() * this.playlist.length);
        } else {
            this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
        }
        
        const nextTrack = this.playlist[this.currentIndex];
        if (nextTrack) {
            this.play(nextTrack);
        }
    }
    
    previousTrack() {
        if (this.playlist.length === 0) return;
        
        if (this.isShuffled) {
            this.currentIndex = Math.floor(Math.random() * this.playlist.length);
        } else {
            this.currentIndex = this.currentIndex > 0 ? this.currentIndex - 1 : this.playlist.length - 1;
        }
        
        const prevTrack = this.playlist[this.currentIndex];
        if (prevTrack) {
            this.play(prevTrack);
        }
    }
    
    setShuffle(shuffled) {
        this.isShuffled = shuffled;
        this.emit('shufflechange', shuffled);
    }
    
    setRepeat(repeated) {
        this.isRepeated = repeated;
        this.emit('repeatchange', repeated);
    }
    
    // Utility methods
    getActiveElement() {
        if (this.currentTrack) {
            const isVideo = this.currentTrack.type === 'show' || this.currentTrack.video_url || this.currentTrack.mp4_link;
            return isVideo ? this.videoElement : this.audioElement;
        }
        return null;
    }
    
    getProgress() {
        if (this.duration > 0) {
            return (this.currentTime / this.duration) * 100;
        }
        return 0;
    }
    
    getTimeRemaining() {
        return Math.max(0, this.duration - this.currentTime);
    }
    
    handleTrackEnd() {
        if (this.isRepeated) {
            this.play(this.currentTrack);
        } else if (window.playerQueue && !window.playerQueue.isEmpty()) {
            // Queue takes priority over playlist
            window.playerQueue.playFromQueue();
        } else if (this.playlist.length > 0) {
            this.nextTrack();
        } else {
            this.stop();
        }
    }
    
    // State persistence: sessionStorage for same-tab navigation, localStorage for cross-session resume
    _saveState() {
        try {
            const state = {
                track: this.currentTrack,
                time: this.currentTime,
                volume: this.volume,
                muted: this.isMuted,
                shuffled: this.isShuffled,
                repeated: this.isRepeated,
                wasPlaying: this.isPlaying
            };
            sessionStorage.setItem('ahoy.player.state', JSON.stringify(state));
            if (this.currentTrack) {
                localStorage.setItem('ahoy.player.lastPlayed', JSON.stringify(state));
            }
        } catch (e) { /* quota exceeded or private mode */ }
    }

    _restoreState() {
        try {
            let raw = sessionStorage.getItem('ahoy.player.state');
            if (!raw) raw = localStorage.getItem('ahoy.player.lastPlayed');
            if (!raw) return;
            const state = JSON.parse(raw);
            if (!state.track) return;

            this.volume = state.volume ?? 1;
            this.isMuted = state.muted ?? false;
            this.isShuffled = state.shuffled ?? false;
            this.isRepeated = state.repeated ?? false;

            this.currentTrack = state.track;
            this.emit('trackchange', state.track);

            const isVideo = state.track.type === 'show' || state.track.video_url || state.track.mp4_link;
            const el = isVideo ? this.videoElement : this.audioElement;
            const src = state.track.audio_url || state.track.full_url || state.track.preview_url || state.track.url || state.track.video_url || state.track.mp4_link;
            if (!src) return;

            el.src = src;
            el.volume = this.volume;
            el.muted = this.isMuted;
            const seekTime = Math.max(0, state.time || 0);
            const wasPlaying = !!state.wasPlaying;

            const onLoaded = () => {
                el.removeEventListener('loadedmetadata', onLoaded);
                el.removeEventListener('error', onError);
                el.currentTime = seekTime;
                this.currentTime = seekTime;
                this.emit('timeupdate', this.currentTime);
                if (wasPlaying && el.play) {
                    const playFn = el.play.bind(el);
                    playFn().catch(err => {
                        if (err && err.name === 'AbortError') return;
                        // Autoplay blocked - user can tap play to resume
                    });
                }
            };
            const onError = () => {
                el.removeEventListener('loadedmetadata', onLoaded);
                el.removeEventListener('error', onError);
            };
            el.addEventListener('loadedmetadata', onLoaded, { once: true });
            el.addEventListener('error', onError, { once: true });

            try { el.load(); } catch (_) {}
        } catch (e) {
            console.warn('Failed to restore player state:', e);
        }
    }

    // Passive listening-time helpers
    _onStarted() {
        this.listening.lastTick = Date.now();
        this._saveState();
    }
    _onPaused() {
        if (this.listening.lastTick) {
            const now = Date.now();
            const delta = Math.max(0, Math.floor((now - this.listening.lastTick) / 1000));
            if (delta > 0) {
                this.listening.totalSec += delta;
                this._persistListening();
            }
        }
        this.listening.lastTick = null;
        this._saveState();
    }
    _onTimeProgress() {
        if (!this.isPlaying) return;
        const now = Date.now();
        if (!this.listening.lastTick) { this.listening.lastTick = now; return; }
        const delta = Math.max(0, Math.floor((now - this.listening.lastTick) / 1000));
        if (delta > 0) {
            this.listening.totalSec += delta;
            this.listening.lastTick = now;
            if (now - this.listening.lastPersist > 5000) {
                this._persistListening();
            }
        }
    }
    _persistListening() {
        this.listening.lastPersist = Date.now();
        try {
            localStorage.setItem('ahoy.listening.totalSec', String(this.listening.totalSec));
        } catch (_) {}
        // Notify listeners each time we persist
        try {
            window.dispatchEvent(new CustomEvent('listening:update', { detail: { totalSeconds: this.listening.totalSec } }));
        } catch (_) {}
        // Also save player state for navigation persistence
        this._saveState();
    }
    
    // Cleanup
    destroy() {
        this.audioElement.remove();
        this.videoElement.remove();
        this.eventListeners.clear();
    }
}

// Create global player instance
window.mediaPlayer = new MediaPlayer();

// Alpine.js data for player components
window.playerData = function() {
    return {
        // Player state
        currentTrack: null,
        isPlaying: false,
        currentTime: 0,
        duration: 0,
        volume: 1,
        isMuted: false,
        isShuffled: false,
        isRepeated: false,
        playlist: [],
        currentIndex: 0,
        
        // UI state
        showPlaylist: false,
        isLoading: false,
        
        // Initialize
        init() {
            this.setupPlayerEvents();
            this.loadInitialData();
        },
        
        setupPlayerEvents() {
            // Listen to global player events
            window.mediaPlayer.on('play', () => {
                this.isPlaying = true;
                this.updateUI();
            });
            
            window.mediaPlayer.on('pause', () => {
                this.isPlaying = false;
                this.updateUI();
            });
            
            window.mediaPlayer.on('timeupdate', (time) => {
                this.currentTime = time;
                this.updateProgress();
            });
            
            window.mediaPlayer.on('durationchange', (duration) => {
                this.duration = duration;
                this.updateUI();
            });
            
            window.mediaPlayer.on('volumechange', (data) => {
                this.volume = data.volume;
                this.isMuted = data.muted;
                this.updateUI();
            });
            
            window.mediaPlayer.on('playlistchange', (playlist) => {
                this.playlist = playlist;
                this.updateUI();
            });
        },
        
        loadInitialData() {
            // Load initial playlist or current track
            this.currentTrack = window.mediaPlayer.currentTrack;
            this.playlist = window.mediaPlayer.playlist;
            this.currentIndex = window.mediaPlayer.currentIndex;
            this.isPlaying = window.mediaPlayer.isPlaying;
            this.volume = window.mediaPlayer.volume;
            this.isMuted = window.mediaPlayer.isMuted;
            this.isShuffled = window.mediaPlayer.isShuffled;
            this.isRepeated = window.mediaPlayer.isRepeated;
        },
        
        // Player controls
        playTrack(track) {
            if (track) {
                window.mediaPlayer.play(track);
            } else {
                window.mediaPlayer.resume();
            }
        },
        
        pauseTrack() {
            window.mediaPlayer.pause();
        },
        
        togglePlay() {
            const mp = window.mediaPlayer;
            if (!mp) return;
            // Use mediaPlayer as source of truth so toggle is correct even if UI state was stale
            if (mp.isPlaying) {
                this.pauseTrack();
            } else {
                const track = mp.currentTrack;
                if (track) {
                    window.mediaPlayer.play(track);
                } else {
                    window.mediaPlayer.resume();
                }
            }
        },
        
        nextTrack() {
            window.mediaPlayer.nextTrack();
        },
        
        previousTrack() {
            window.mediaPlayer.previousTrack();
        },
        
        seekTo(event) {
            const progressBar = event.currentTarget;
            const rect = progressBar.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const percentage = clickX / rect.width;
            const newTime = percentage * this.duration;
            
            window.mediaPlayer.seekTo(newTime);
        },
        
        setVolume(event) {
            const volumeBar = event.currentTarget;
            const rect = volumeBar.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const volume = Math.max(0, Math.min(1, clickX / rect.width));
            
            window.mediaPlayer.setVolume(volume);
        },
        
        toggleMute() {
            window.mediaPlayer.toggleMute();
        },
        
        toggleShuffle() {
            window.mediaPlayer.setShuffle(!this.isShuffled);
        },
        
        toggleRepeat() {
            window.mediaPlayer.setRepeat(!this.isRepeated);
        },
        
        // Playlist management
        addToPlaylist(track) {
            window.mediaPlayer.addToPlaylist(track);
        },
        
        removeFromPlaylist(index) {
            window.mediaPlayer.removeFromPlaylist(index);
        },
        
        playPlaylistItem(index) {
            this.currentIndex = index;
            const track = this.playlist[index];
            if (track) {
                this.playTrack(track);
            }
        },
        
        // UI updates
        updateUI() {
            // Update any UI elements that need refreshing
            this.$nextTick(() => {
                // Force reactivity updates
            });
        },
        
        updateProgress() {
            // Update progress bars
            const progressBars = document.querySelectorAll('.progress-fill');
            const progress = this.getProgress();
            
            progressBars.forEach(bar => {
                bar.style.width = `${progress}%`;
            });
        },
        
        getProgress() {
            if (this.duration > 0) {
                return (this.currentTime / this.duration) * 100;
            }
            return 0;
        },
        
        // Utility functions
        formatTime(seconds) {
            if (!seconds || isNaN(seconds)) return '0:00';
            
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        },
        
        formatDuration(seconds) {
            return this.formatTime(seconds);
        },

        toggleBookmark(mediaId) {
            const item = { id: mediaId, type: 'track' };
            // Assuming toggle and keyOf are defined elsewhere or will be added.
            // For now, just a placeholder.
            // window.mediaPlayer.toggleBookmark(item);
        },

        isBookmarked(mediaId) {
            // Assuming keyOf and state are defined elsewhere or will be added.
            // For now, just a placeholder.
            // return window.mediaPlayer.isBookmarked(mediaId);
            return false; // Placeholder
        }
    };
};

// Export for global use
window.PlayerControls = {
    play: (track) => window.mediaPlayer.play(track),
    pause: () => window.mediaPlayer.pause(),
    resume: () => window.mediaPlayer.resume(),
    stop: () => window.mediaPlayer.stop(),
    next: () => window.mediaPlayer.nextTrack(),
    previous: () => window.mediaPlayer.previousTrack(),
    seek: (time) => window.mediaPlayer.seekTo(time),
    setVolume: (volume) => window.mediaPlayer.setVolume(volume),
    setMuted: (muted) => window.mediaPlayer.setMuted(muted),
    toggleMute: () => window.mediaPlayer.toggleMute(),
    setShuffle: (shuffled) => window.mediaPlayer.setShuffle(shuffled),
    setRepeat: (repeated) => window.mediaPlayer.setRepeat(repeated)
};
