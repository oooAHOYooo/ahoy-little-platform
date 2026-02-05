// Ahoy Indie Media - Background Audio Controller
// Provides ambient/focus audio that plays independently of the main player

class BackgroundAudioController {
    constructor() {
        // Dual audio elements for gapless looping
        this._audio1 = document.createElement('audio');
        this._audio2 = document.createElement('audio');
        this._activeAudio = this._audio1;
        this._nextAudio = this._audio2;

        // Setup audio elements
        [this._audio1, this._audio2].forEach(audio => {
            audio.preload = 'auto';
            audio.loop = false; // We handle looping ourselves for gapless
            try { audio.setAttribute('playsinline', ''); } catch (_) {}
            audio.style.display = 'none';
            document.body.appendChild(audio);
        });

        // State
        this.currentMode = null;
        this.isPlaying = false;
        this.volume = 0.5;
        this.intensity = 'medium'; // 'low' | 'medium' | 'high'
        this.isDucked = false;
        this.duckMode = 'duck'; // 'duck' | 'pause'
        this.duckLevel = 0.1; // Volume level when ducked (10%)

        // Internal state
        this._preDuckVolume = null;
        this._wasPlayingBeforePause = false;
        this._isPreloading = false;
        this._lastTrackUrl = null;
        this._fadeInterval = null;
        this._eventListeners = new Map();

        this._setupEventListeners();
        this._listenToMainPlayer();
        this._restoreState();
    }

    // Event emitter pattern (matches player.js)
    on(event, callback) {
        if (!this._eventListeners.has(event)) {
            this._eventListeners.set(event, new Set());
        }
        this._eventListeners.get(event).add(callback);
    }

    off(event, callback) {
        if (this._eventListeners.has(event)) {
            this._eventListeners.get(event).delete(callback);
        }
    }

    emit(event, data) {
        if (this._eventListeners.has(event)) {
            this._eventListeners.get(event).forEach(callback => {
                try { callback(data); } catch (e) { console.warn('BgAudio event handler error:', e); }
            });
        }
    }

    _setupEventListeners() {
        // Active audio events
        this._audio1.addEventListener('timeupdate', () => this._onTimeUpdate(this._audio1));
        this._audio2.addEventListener('timeupdate', () => this._onTimeUpdate(this._audio2));

        this._audio1.addEventListener('ended', () => this._onEnded(this._audio1));
        this._audio2.addEventListener('ended', () => this._onEnded(this._audio2));

        this._audio1.addEventListener('error', (e) => this._onError(e));
        this._audio2.addEventListener('error', (e) => this._onError(e));

        this._audio1.addEventListener('canplaythrough', () => this.emit('canplaythrough'));
        this._audio2.addEventListener('canplaythrough', () => this.emit('canplaythrough'));
    }

    _onTimeUpdate(audio) {
        if (audio !== this._activeAudio) return;

        // Preload next track when ~10 seconds remaining
        const remaining = audio.duration - audio.currentTime;
        if (remaining <= 10 && remaining > 0 && !this._isPreloading && this.isPlaying) {
            this._preloadNext();
        }

        this.emit('timeupdate', { currentTime: audio.currentTime, duration: audio.duration });
    }

    _onEnded(audio) {
        if (audio !== this._activeAudio) return;

        // Swap to preloaded track for gapless playback
        if (this._nextAudio.src && this._nextAudio.readyState >= 2) {
            this._swapAndPlay();
        } else {
            // Fallback: reload current mode
            this._playCurrentMode();
        }
    }

    _onError(e) {
        console.warn('Background audio error:', e);
        this.emit('error', e);
    }

    _preloadNext() {
        if (!this.currentMode || this._isPreloading) return;

        this._isPreloading = true;
        const nextUrl = this._pickRandomTrack();

        if (nextUrl) {
            this._nextAudio.src = this._getAudioUrl(nextUrl);
            this._nextAudio.load();
        }
    }

    _swapAndPlay() {
        // Swap audio elements
        const temp = this._activeAudio;
        this._activeAudio = this._nextAudio;
        this._nextAudio = temp;

        // Play the new active audio
        this._activeAudio.volume = this._getEffectiveVolume();
        this._activeAudio.play().catch(e => {
            if (e.name !== 'AbortError') {
                console.warn('Background audio swap play failed:', e);
            }
        });

        this._isPreloading = false;
        this.emit('trackchange');
    }

    _pickRandomTrack() {
        if (!this.currentMode || !this.currentMode.audioPool) return null;

        const pool = this.currentMode.audioPool[this.intensity];
        if (!pool || pool.length === 0) return null;

        // Pick random track, avoiding the same track twice in a row
        let attempts = 0;
        let url = null;
        while (attempts < 5) {
            const idx = Math.floor(Math.random() * pool.length);
            url = pool[idx];
            if (url !== this._lastTrackUrl || pool.length === 1) {
                break;
            }
            attempts++;
        }

        this._lastTrackUrl = url;
        return url;
    }

    // Convert external URLs to proxy URLs for local testing (matches player.js pattern)
    _getAudioUrl(url) {
        if (!url) return url;
        const isLocalhost = window.location.hostname === 'localhost' ||
                           window.location.hostname === '127.0.0.1';
        const isExternal = url.startsWith('https://') &&
                          (url.includes('s3') || url.includes('storage.googleapis.com') ||
                           url.includes('cdn.ahoy') || url.includes('ahoycollection'));

        if (isLocalhost && isExternal) {
            return `/proxy/audio?url=${encodeURIComponent(url)}`;
        }
        return url;
    }

    _getEffectiveVolume() {
        return this.isDucked ? this.duckLevel : this.volume;
    }

    _setEffectiveVolume(vol, animate = true) {
        const targetVol = Math.max(0, Math.min(1, vol));

        if (animate) {
            this._fadeVolume(targetVol, 300);
        } else {
            this._activeAudio.volume = targetVol;
            this._nextAudio.volume = targetVol;
        }
    }

    _fadeVolume(targetVol, durationMs) {
        if (this._fadeInterval) {
            clearInterval(this._fadeInterval);
        }

        const startVol = this._activeAudio.volume;
        const diff = targetVol - startVol;
        const steps = 15;
        const stepDuration = durationMs / steps;
        let step = 0;

        this._fadeInterval = setInterval(() => {
            step++;
            const progress = step / steps;
            const newVol = startVol + (diff * progress);
            this._activeAudio.volume = newVol;
            this._nextAudio.volume = newVol;

            if (step >= steps) {
                clearInterval(this._fadeInterval);
                this._fadeInterval = null;
            }
        }, stepDuration);
    }

    // Main player coordination
    _listenToMainPlayer() {
        // Wait for mediaPlayer to be available
        const checkPlayer = () => {
            if (window.mediaPlayer) {
                window.mediaPlayer.on('play', () => this._onMainPlayerPlay());
                window.mediaPlayer.on('pause', () => this._onMainPlayerStop());
                window.mediaPlayer.on('ended', () => this._onMainPlayerStop());
            } else {
                setTimeout(checkPlayer, 500);
            }
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', checkPlayer);
        } else {
            checkPlayer();
        }
    }

    _onMainPlayerPlay() {
        if (!this.isPlaying) return;

        if (this.duckMode === 'duck') {
            this._preDuckVolume = this.volume;
            this._setEffectiveVolume(this.duckLevel);
            this.isDucked = true;
            this.emit('ducked', true);
        } else {
            // Pause mode
            this._wasPlayingBeforePause = this.isPlaying;
            this.pause();
        }
    }

    _onMainPlayerStop() {
        if (this.duckMode === 'duck' && this.isDucked) {
            const restoreVol = this._preDuckVolume != null ? this._preDuckVolume : this.volume;
            this._setEffectiveVolume(restoreVol);
            this.isDucked = false;
            this._preDuckVolume = null;
            this.emit('ducked', false);
        } else if (this.duckMode === 'pause' && this._wasPlayingBeforePause) {
            this._wasPlayingBeforePause = false;
            this.resume();
        }
    }

    // Public API
    async play(mode) {
        if (!mode) return;

        this.currentMode = mode;
        this._playCurrentMode();

        // Dispatch analytics event
        document.dispatchEvent(new CustomEvent('background_audio_started', {
            detail: { modeId: mode.id, intensity: this.intensity }
        }));
    }

    _playCurrentMode() {
        const trackUrl = this._pickRandomTrack();
        if (!trackUrl) {
            console.warn('No audio tracks available for mode:', this.currentMode?.id);
            return;
        }

        this._activeAudio.src = this._getAudioUrl(trackUrl);
        this._activeAudio.volume = this._getEffectiveVolume();
        this._activeAudio.load();

        this._activeAudio.play().then(() => {
            this.isPlaying = true;
            this._saveState();
            this.emit('play', this.currentMode);
        }).catch(e => {
            if (e.name !== 'AbortError') {
                console.warn('Background audio play failed:', e);
                this.emit('error', e);
            }
        });
    }

    pause() {
        this._activeAudio.pause();
        this.isPlaying = false;
        this._saveState();
        this.emit('pause');
    }

    resume() {
        if (!this.currentMode) return;

        this._activeAudio.play().then(() => {
            this.isPlaying = true;
            this._saveState();
            this.emit('play', this.currentMode);
        }).catch(e => {
            if (e.name !== 'AbortError') {
                console.warn('Background audio resume failed:', e);
            }
        });
    }

    stop() {
        this._activeAudio.pause();
        this._activeAudio.currentTime = 0;
        this._nextAudio.pause();
        this._nextAudio.currentTime = 0;
        this.isPlaying = false;
        this.currentMode = null;
        this._isPreloading = false;
        this._saveState();
        this.emit('stop');
    }

    setVolume(vol) {
        this.volume = Math.max(0, Math.min(1, vol));
        if (!this.isDucked) {
            this._setEffectiveVolume(this.volume, false);
        }
        this._saveState();
        this.emit('volumechange', this.volume);
    }

    setIntensity(level) {
        if (!['low', 'medium', 'high'].includes(level)) return;

        const changed = this.intensity !== level;
        this.intensity = level;
        this._saveState();
        this.emit('intensitychange', level);

        // If playing, preload a track with new intensity
        if (changed && this.isPlaying) {
            this._isPreloading = false;
            this._preloadNext();
        }
    }

    setDuckMode(mode) {
        if (!['duck', 'pause'].includes(mode)) return;
        this.duckMode = mode;
        this._saveState();
        this.emit('duckmodechange', mode);
    }

    // Persistence
    _saveState() {
        try {
            const state = {
                modeId: this.currentMode?.id || null,
                intensity: this.intensity,
                volume: this.volume,
                duckMode: this.duckMode
            };
            localStorage.setItem('ahoy.bgAudio.v1', JSON.stringify(state));
        } catch (e) {
            console.warn('Failed to save background audio state:', e);
        }
    }

    _restoreState() {
        try {
            const stored = localStorage.getItem('ahoy.bgAudio.v1');
            if (!stored) return;

            const state = JSON.parse(stored);
            if (state.intensity) this.intensity = state.intensity;
            if (typeof state.volume === 'number') this.volume = state.volume;
            if (state.duckMode) this.duckMode = state.duckMode;

            // Don't auto-play on restore (requires user gesture)
            // But store modeId so UI can show last used mode
            this._restoredModeId = state.modeId;

            this.emit('restored', state);
        } catch (e) {
            console.warn('Failed to restore background audio state:', e);
        }
    }

    getRestoredModeId() {
        return this._restoredModeId || null;
    }
}

// Create global singleton
window.backgroundAudioController = new BackgroundAudioController();
