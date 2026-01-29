// Ahoy Indie Media - Player Queue System
// Manages play queue separately from playlist, auto-pauses on video/new content

(function() {
    'use strict';

    class PlayerQueue {
        constructor() {
            this.items = [];
            this.history = [];
            this.maxHistory = 50;
            this._pauseOnAdd = false; // when true, pause current track when adding
            this._restoreState();
        }

        _saveState() {
            try {
                sessionStorage.setItem('ahoy.queue', JSON.stringify(this.items));
            } catch (e) { /* quota or private mode */ }
        }

        _restoreState() {
            try {
                const raw = sessionStorage.getItem('ahoy.queue');
                if (raw) {
                    this.items = JSON.parse(raw) || [];
                }
            } catch (e) { /* ignore */ }
        }

        // Get current queue
        getQueue() {
            return [...this.items];
        }

        // Get history
        getHistory() {
            return [...this.history];
        }

        // Add track(s) to play next (after current)
        playNext(tracks) {
            const arr = Array.isArray(tracks) ? tracks : [tracks];
            this.items.unshift(...arr);
            this._emit('queue:changed', { action: 'playNext', items: arr });
            if (this._pauseOnAdd && arr.length > 0) this._pauseCurrent();
            return this;
        }

        // Add track(s) to end of queue
        addToQueue(tracks) {
            const arr = Array.isArray(tracks) ? tracks : [tracks];
            this.items.push(...arr);
            this._emit('queue:changed', { action: 'add', items: arr });
            if (this._pauseOnAdd && arr.length > 0) this._pauseCurrent();
            return this;
        }

        // Replace entire queue
        replace(tracks) {
            const arr = Array.isArray(tracks) ? tracks : [tracks];
            this.items = [...arr];
            this._emit('queue:changed', { action: 'replace', items: arr });
            return this;
        }

        // Remove track at index
        remove(index) {
            if (index >= 0 && index < this.items.length) {
                const removed = this.items.splice(index, 1);
                this._emit('queue:changed', { action: 'remove', items: removed, index });
            }
            return this;
        }

        // Clear queue
        clear() {
            this.items = [];
            this._emit('queue:changed', { action: 'clear', items: [] });
            return this;
        }

        // Move track within queue
        move(fromIndex, toIndex) {
            if (fromIndex < 0 || fromIndex >= this.items.length) return this;
            if (toIndex < 0 || toIndex >= this.items.length) return this;
            const [item] = this.items.splice(fromIndex, 1);
            this.items.splice(toIndex, 0, item);
            this._emit('queue:changed', { action: 'move', fromIndex, toIndex });
            return this;
        }

        // Get and remove next track from queue
        shift() {
            const track = this.items.shift();
            if (track) {
                this._addToHistory(track);
                this._emit('queue:changed', { action: 'shift', items: [track] });
            }
            return track || null;
        }

        // Peek at next track without removing
        peek() {
            return this.items[0] || null;
        }

        // Check if queue is empty
        isEmpty() {
            return this.items.length === 0;
        }

        // Get queue length
        get length() {
            return this.items.length;
        }

        // Enable/disable pause on add
        setPauseOnAdd(val) {
            this._pauseOnAdd = !!val;
        }

        // Add track to history
        _addToHistory(track) {
            this.history.unshift(track);
            if (this.history.length > this.maxHistory) {
                this.history.pop();
            }
        }

        // Pause current playback
        _pauseCurrent() {
            if (window.mediaPlayer && typeof window.mediaPlayer.pause === 'function') {
                window.mediaPlayer.pause();
            }
        }

        // Emit event and persist
        _emit(name, detail) {
            try {
                document.dispatchEvent(new CustomEvent(name, { detail }));
            } catch (e) { /* ignore */ }
            this._saveState();
        }

        // Play next from queue (called when track ends if queue has items)
        playFromQueue() {
            const next = this.shift();
            if (next && window.mediaPlayer) {
                window.mediaPlayer.play(next);
                return true;
            }
            return false;
        }
    }

    // Create global instance
    const queue = new PlayerQueue();
    window.playerQueue = queue;

    // Legacy Queue object for backward compatibility
    window.Queue = {
        items: queue.items,
        replace: (items) => queue.replace(items),
        append: (items) => queue.addToQueue(items),
        playNext: (items) => queue.playNext(items)
    };

    // Note: Queue auto-advance is handled in player.js handleTrackEnd()
    // which checks window.playerQueue.isEmpty() before falling back to playlist

    // --- Auto-pause audio when external videos play ---
    function pauseAudioOnVideoPlay(videoEl) {
        const mp = window.mediaPlayer;
        if (!mp) return;
        // Don't pause if this is the mediaPlayer's own video
        if (videoEl === mp.videoElement) return;
        // Pause audio if playing
        if (mp.isPlaying && mp.audioElement && !mp.audioElement.paused) {
            mp.pause();
            try {
                document.dispatchEvent(new CustomEvent('ahoy:toast', {
                    detail: 'Audio paused for video playback'
                }));
            } catch (e) { /* ignore */ }
        }
    }

    // Listen for play events on all video elements
    function observeVideos() {
        // Handle existing videos
        document.querySelectorAll('video').forEach(v => {
            if (!v._ahoyObserved) {
                v._ahoyObserved = true;
                v.addEventListener('play', () => pauseAudioOnVideoPlay(v));
            }
        });

        // Watch for new videos added to DOM
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeName === 'VIDEO') {
                        if (!node._ahoyObserved) {
                            node._ahoyObserved = true;
                            node.addEventListener('play', () => pauseAudioOnVideoPlay(node));
                        }
                    }
                    // Check children
                    if (node.querySelectorAll) {
                        node.querySelectorAll('video').forEach(v => {
                            if (!v._ahoyObserved) {
                                v._ahoyObserved = true;
                                v.addEventListener('play', () => pauseAudioOnVideoPlay(v));
                            }
                        });
                    }
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Initialize when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', observeVideos);
    } else {
        observeVideos();
    }

    // Listen for playlist creation events (legacy support)
    document.addEventListener('playlist:created', (e) => {
        const pl = e.detail;
        if (!pl || !Array.isArray(pl.items)) return;
        if (pl._queueMode === 'replace') queue.replace(pl.items);
        if (pl._queueMode === 'append') queue.addToQueue(pl.items);
        if (pl._queueMode === 'next') queue.playNext(pl.items);
    });
})();
