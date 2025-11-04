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
    }
    
    initializePlayer() {
        // Create audio element for music
        this.audioElement = document.createElement('audio');
        this.audioElement.preload = 'metadata';
        this.audioElement.style.display = 'none';
        document.body.appendChild(this.audioElement);
        
        // Create video element for shows
        this.videoElement = document.createElement('video');
        this.videoElement.preload = 'metadata';
        this.videoElement.style.display = 'none';
        document.body.appendChild(this.videoElement);
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Audio events
        this.audioElement.addEventListener('loadedmetadata', () => {
            this.duration = this.audioElement.duration;
            this.emit('durationchange', this.duration);
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
        this.videoElement.addEventListener('loadedmetadata', () => {
            this.duration = this.videoElement.duration;
            this.emit('durationchange', this.duration);
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
        this.currentTrack = track;
        
        // Determine which element to use
        const isVideo = track.type === 'show' || track.video_url || track.mp4_link;
        const mediaElement = isVideo ? this.videoElement : this.audioElement;
        
        // Pause other element
        if (isVideo) {
            this.audioElement.pause();
        } else {
            this.videoElement.pause();
        }
        
        // Set source
        const source = isVideo ? (track.video_url || track.mp4_link) : (track.audio_url || track.preview_url);
        mediaElement.src = source;
        
        // Set properties
        mediaElement.volume = this.volume;
        mediaElement.muted = this.isMuted;
        
        // Play
        mediaElement.play().then(() => {
            this.isPlaying = true;
            this.emit('play');
        }).catch(error => {
            console.error('Error playing media:', error);
            this.emit('error', error);
        });
    }
    
    pause() {
        if (this.audioElement && !this.audioElement.paused) {
            this.audioElement.pause();
        }
        if (this.videoElement && !this.videoElement.paused) {
            this.videoElement.pause();
        }
    }
    
    resume() {
        const activeElement = this.getActiveElement();
        if (activeElement) {
            activeElement.play().catch(error => {
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
        this.play(nextTrack);
    }
    
    previousTrack() {
        if (this.playlist.length === 0) return;
        
        if (this.isShuffled) {
            this.currentIndex = Math.floor(Math.random() * this.playlist.length);
        } else {
            this.currentIndex = this.currentIndex > 0 ? this.currentIndex - 1 : this.playlist.length - 1;
        }
        
        const prevTrack = this.playlist[this.currentIndex];
        this.play(prevTrack);
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
        } else if (this.playlist.length > 0) {
            this.nextTrack();
        } else {
            this.stop();
        }
    }
    
    // Passive listening-time helpers
    _onStarted() {
        this.listening.lastTick = Date.now();
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
            if (this.isPlaying) {
                this.pauseTrack();
            } else {
                this.playTrack();
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
