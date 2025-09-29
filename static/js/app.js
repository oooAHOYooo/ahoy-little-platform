// Ahoy Indie Media - Main JavaScript

// Global state
window.ahoyApp = {
    user: null,
    isLoggedIn: false,
    currentTrack: null,
    isPlaying: false,
    currentTime: 0,
    volume: 1,
    isMuted: false,
    playlist: [],
    currentIndex: 0,
    isShuffled: false,
    isRepeated: false,
    isLiked: false
};

// Navbar component for Alpine.js
function navbar() {
    return {
        isLoggedIn: false,
        userProfile: {},
        isLoading: false,
        searchQuery: '',
        darkMode: false,
        autoPlay: false,
        notifications: true,
        
        init() {
            console.log('Navbar initialized');
            // Check auth status when component initializes
            this.checkAuthStatus();
            // Load settings from localStorage
            this.loadSettings();
        },
        
        async checkAuthStatus() {
            try {
                const response = await fetch('/api/user/profile');
                if (response.ok) {
                    const user = await response.json();
                    this.isLoggedIn = true;
                    this.userProfile = user;
                } else {
                    this.isLoggedIn = false;
                    this.userProfile = {};
                }
            } catch (error) {
                this.isLoggedIn = false;
                this.userProfile = {};
            }
        },
        
        
        async logout() {
            try {
                await fetch('/api/user/logout', { method: 'POST' });
                this.isLoggedIn = false;
                this.userProfile = {};
                this.showNotification('You have been signed out', 'info');
                // Refresh the page to update all components
                window.location.reload();
            } catch (error) {
                console.error('Logout failed:', error);
            }
        },
        
        
        performSearch() {
            if (this.searchQuery.trim()) {
                // Redirect to search results page
                window.location.href = `/search?q=${encodeURIComponent(this.searchQuery)}`;
            }
        },
        
        clearSearch() {
            this.searchQuery = '';
        },
        
        clearSearch() {
            this.searchQuery = '';
        },
        
        loadSettings() {
            // Load settings from localStorage
            const savedSettings = localStorage.getItem('ahoy_settings');
            if (savedSettings) {
                try {
                    const settings = JSON.parse(savedSettings);
                    this.darkMode = settings.darkMode || false;
                    this.autoPlay = settings.autoPlay || false;
                    this.notifications = settings.notifications !== false;
                    this.applySettings();
                } catch (error) {
                    console.error('Error loading settings:', error);
                }
            }
        },
        
        saveSettings() {
            const settings = {
                darkMode: this.darkMode,
                autoPlay: this.autoPlay,
                notifications: this.notifications
            };
            localStorage.setItem('ahoy_settings', JSON.stringify(settings));
        },
        
        applySettings() {
            // Apply dark mode
            if (this.darkMode) {
                document.documentElement.classList.add('dark-mode');
            } else {
                document.documentElement.classList.remove('dark-mode');
            }
        },
        
        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            this.applySettings();
            this.saveSettings();
        },
        
        toggleAutoPlay() {
            this.autoPlay = !this.autoPlay;
            this.saveSettings();
            // Notify other components about the change
            window.dispatchEvent(new CustomEvent('autoplay-changed', { 
                detail: { enabled: this.autoPlay } 
            }));
        },
        
        toggleNotifications() {
            this.notifications = !this.notifications;
            this.saveSettings();
            // Request notification permission if enabling
            if (this.notifications && 'Notification' in window) {
                Notification.requestPermission();
            }
        },
        
        toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log('Error attempting to enable fullscreen:', err);
                });
            } else {
                document.exitFullscreen();
            }
        },
        
        openLibrary() {
            // Implement library functionality
            console.log('Opening library...');
        },
        
        openPlaylists() {
            // Implement playlists functionality
            console.log('Opening playlists...');
        },
        
        openLiked() {
            // Implement liked items functionality
            console.log('Opening liked items...');
        }
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Hide loading indicator once Alpine.js is loaded
document.addEventListener('alpine:init', function() {
    // Hide loading indicator
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
});

// Fallback: hide loading indicator after 3 seconds
setTimeout(function() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}, 3000);

function initializeApp() {
    // Check if user is logged in
    checkAuthStatus();
    
    // Initialize global player
    initializeGlobalPlayer();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    loadInitialData();
}

function checkAuthStatus() {
    // Check if user is logged in via session
    fetch('/api/user/profile')
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Not authenticated');
        })
        .then(user => {
            window.ahoyApp.user = user;
            window.ahoyApp.isLoggedIn = true;
            updateUIForLoggedInUser();
        })
        .catch(error => {
            window.ahoyApp.user = null;
            window.ahoyApp.isLoggedIn = false;
            updateUIForLoggedOutUser();
            // Don't show error for unauthenticated users - this is normal
        });
}

function updateUIForLoggedInUser() {
    // Update navigation to show user menu
    const navUser = document.querySelector('.nav-user');
    if (navUser) {
        navUser.style.display = 'block';
    }
    
    // Update any user-specific UI elements
    const userElements = document.querySelectorAll('[x-data*="navbar"]');
    userElements.forEach(element => {
        if (element._x_dataStack) {
            element._x_dataStack[0].isLoggedIn = true;
            element._x_dataStack[0].userProfile = window.ahoyApp.user;
        }
    });
}

function updateUIForLoggedOutUser() {
    // Update navigation to show auth buttons
    const navUser = document.querySelector('.nav-user');
    if (navUser) {
        navUser.style.display = 'block';
    }
    
    // Update any user-specific UI elements
    const userElements = document.querySelectorAll('[x-data*="navbar"]');
    userElements.forEach(element => {
        if (element._x_dataStack) {
            element._x_dataStack[0].isLoggedIn = false;
            element._x_dataStack[0].userProfile = {};
        }
    });
}

function initializeGlobalPlayer() {
    // Initialize global player state
    window.globalPlayer = {
        playTrack: function(track) {
            window.ahoyApp.currentTrack = track;
            window.ahoyApp.isPlaying = true;
            
            // Update global player UI
            updateGlobalPlayerUI();
            
            // Play the track
            playMedia(track);
        },
        
        pauseTrack: function() {
            window.ahoyApp.isPlaying = false;
            pauseMedia();
            updateGlobalPlayerUI();
        },
        
        resumeTrack: function() {
            window.ahoyApp.isPlaying = true;
            resumeMedia();
            updateGlobalPlayerUI();
        },
        
        nextTrack: function() {
            if (window.ahoyApp.playlist.length > 0) {
                window.ahoyApp.currentIndex = (window.ahoyApp.currentIndex + 1) % window.ahoyApp.playlist.length;
                const nextTrack = window.ahoyApp.playlist[window.ahoyApp.currentIndex];
                this.playTrack(nextTrack);
            }
        },
        
        previousTrack: function() {
            if (window.ahoyApp.playlist.length > 0) {
                window.ahoyApp.currentIndex = window.ahoyApp.currentIndex > 0 
                    ? window.ahoyApp.currentIndex - 1 
                    : window.ahoyApp.playlist.length - 1;
                const prevTrack = window.ahoyApp.playlist[window.ahoyApp.currentIndex];
                this.playTrack(prevTrack);
            }
        }
    };
}

function setupEventListeners() {
    // Global keyplaylist shortcuts
    document.addEventListener('keydown', handleKeyplaylistShortcuts);
    
    // Window events
    window.addEventListener('beforeunload', saveUserState);
    
    // Media events
    setupMediaEventListeners();
}

function handleKeyplaylistShortcuts(event) {
    // Check if user is typing in input fields
    const isInputActive = event.target.matches('input, textarea, select, [contenteditable="true"]') || 
                         event.target.closest('input, textarea, select, [contenteditable="true"]');
    
    // Disable all shortcuts if user is typing
    if (isInputActive) {
        return;
    }
    
    // Space bar - play/pause
    if (event.code === 'Space') {
        event.preventDefault();
        togglePlayPause();
    }
    
    // Arrow keys - next/previous (for hero slides when not in global player)
    if (event.code === 'ArrowRight') {
        event.preventDefault();
        // Check if we're on the homepage and hero is visible
        const heroFeed = document.querySelector('.hero-feed');
        if (heroFeed && heroFeed.offsetParent !== null) {
            // Navigate hero slides
            if (window.homePage && typeof window.homePage.nextHero === 'function') {
                window.homePage.nextHero();
            }
        } else {
            // Navigate global player
            window.globalPlayer.nextTrack();
        }
    }
    
    if (event.code === 'ArrowLeft') {
        event.preventDefault();
        // Check if we're on the homepage and hero is visible
        const heroFeed = document.querySelector('.hero-feed');
        if (heroFeed && heroFeed.offsetParent !== null) {
            // Navigate hero slides
            if (window.homePage && typeof window.homePage.prevHero === 'function') {
                window.homePage.prevHero();
            }
        } else {
            // Navigate global player
            window.globalPlayer.previousTrack();
        }
    }
    
    // M key - mute/unmute
    if (event.code === 'KeyM') {
        event.preventDefault();
        toggleMute();
    }
    
    // S key - shuffle
    if (event.code === 'KeyS') {
        event.preventDefault();
        toggleShuffle();
    }
    
    // R key - repeat
    if (event.code === 'KeyR') {
        event.preventDefault();
        toggleRepeat();
    }
}

function setupMediaEventListeners() {
    // Listen for media events from audio/video elements
    document.addEventListener('play', function(event) {
        if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
            window.ahoyApp.isPlaying = true;
            updateGlobalPlayerUI();
        }
    });
    
    document.addEventListener('pause', function(event) {
        if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
            window.ahoyApp.isPlaying = false;
            updateGlobalPlayerUI();
        }
    });
    
    document.addEventListener('ended', function(event) {
        if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
            window.ahoyApp.isPlaying = false;
            window.globalPlayer.nextTrack();
        }
    });
}

function playMedia(track) {
    // Set current track in global state
    window.ahoyApp.currentTrack = track;
    window.ahoyApp.isPlaying = true;
    
    // Update global player UI
    updateGlobalPlayerUI();
    
    // Create or update audio/video element
    let mediaElement = document.querySelector('#global-media-player');
    
    if (!mediaElement) {
        // Create appropriate element based on track type
        if (track.type === 'show') {
            mediaElement = document.createElement('video');
            mediaElement.controls = true;
            mediaElement.style.width = '100%';
            mediaElement.style.maxWidth = '800px';
            mediaElement.style.height = 'auto';
        } else {
            mediaElement = document.createElement('audio');
            mediaElement.style.display = 'none';
        }
        mediaElement.id = 'global-media-player';
        document.body.appendChild(mediaElement);
    }
    
    // Set source based on track type
    if (track.type === 'music' || !track.type) {
        mediaElement.src = track.audio_url || track.preview_url;
    } else if (track.type === 'show') {
        mediaElement.src = track.video_url || track.mp4_link;
    }
    
    // Set volume
    mediaElement.volume = window.ahoyApp.volume;
    mediaElement.muted = window.ahoyApp.isMuted;
    
    // Play
    mediaElement.play().catch(error => {
        console.error('Error playing media:', error);
    });
}

function pauseMedia() {
    const mediaElement = document.querySelector('#global-media-player');
    if (mediaElement) {
        mediaElement.pause();
    }
}

function resumeMedia() {
    const mediaElement = document.querySelector('#global-media-player');
    if (mediaElement) {
        mediaElement.play().catch(error => {
            console.error('Error resuming media:', error);
        });
    }
}

function togglePlayPause() {
    if (window.ahoyApp.isPlaying) {
        window.globalPlayer.pauseTrack();
    } else {
        window.globalPlayer.resumeTrack();
    }
}

function toggleMute() {
    window.ahoyApp.isMuted = !window.ahoyApp.isMuted;
    
    const mediaElement = document.querySelector('#global-media-player');
    if (mediaElement) {
        mediaElement.muted = window.ahoyApp.isMuted;
    }
    
    updateGlobalPlayerUI();
}

function toggleShuffle() {
    window.ahoyApp.isShuffled = !window.ahoyApp.isShuffled;
    
    if (window.ahoyApp.isShuffled && window.ahoyApp.playlist.length > 0) {
        shufflePlaylist();
    }
    
    updateGlobalPlayerUI();
}

function toggleRepeat() {
    window.ahoyApp.isRepeated = !window.ahoyApp.isRepeated;
    updateGlobalPlayerUI();
}

function shufflePlaylist() {
    const playlist = window.ahoyApp.playlist;
    for (let i = playlist.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [playlist[i], playlist[j]] = [playlist[j], playlist[i]];
    }
}

function updateGlobalPlayerUI() {
    // Update global player UI elements
    const playerElements = document.querySelectorAll('[x-data*="globalPlayer"]');
    playerElements.forEach(element => {
        if (element._x_dataStack) {
            const data = element._x_dataStack[0];
            data.currentTrack = window.ahoyApp.currentTrack;
            data.isPlaying = window.ahoyApp.isPlaying;
            data.isMuted = window.ahoyApp.isMuted;
            data.isShuffled = window.ahoyApp.isShuffled;
            data.isRepeated = window.ahoyApp.isRepeated;
        }
    });
}

function loadInitialData() {
    // Load any initial data needed for the app
    loadDailyPlaylist();
}

async function loadDailyPlaylist() {
    try {
        const response = await fetch('/api/daily-playlist');
        const data = await response.json();
        
        if (data.playlist && data.playlist.length > 0) {
            window.ahoyApp.playlist = data.playlist;
        }
    } catch (error) {
        console.error('Error loading daily playlist:', error);
    }
}

function saveUserState() {
    // Save user state before page unload
    if (window.ahoyApp.isLoggedIn) {
        localStorage.setItem('ahoy_user_state', JSON.stringify({
            currentTrack: window.ahoyApp.currentTrack,
            playlist: window.ahoyApp.playlist,
            currentIndex: window.ahoyApp.currentIndex,
            volume: window.ahoyApp.volume,
            isMuted: window.ahoyApp.isMuted,
            isShuffled: window.ahoyApp.isShuffled,
            isRepeated: window.ahoyApp.isRepeated
        }));
    }
}

function loadUserState() {
    // Load saved user state
    const savedState = localStorage.getItem('ahoy_user_state');
    if (savedState) {
        try {
            const state = JSON.parse(savedState);
            Object.assign(window.ahoyApp, state);
            updateGlobalPlayerUI();
        } catch (error) {
            console.error('Error loading user state:', error);
        }
    }
}

// Utility functions


function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// API helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Search functionality
function performSearch(query) {
    if (!query || query.trim().length < 2) return;
    
    // Redirect to search results or update current page
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        bottom: '60px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontSize: '14px',
        fontWeight: '500',
        zIndex: '10000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        maxWidth: '300px',
        wordWrap: 'break-word'
    });
    
    // Set background color based on type
    const colors = {
        info: '#3b82f6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Add to DOM
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showNotification('An error occurred. Please try again.', 'error');
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showNotification('An error occurred. Please try again.', 'error');
});

// Global Player Component
function globalPlayer() {
    return {
        // State
        currentTrack: null,
        isPlaying: false,
        currentTime: 0,
        volume: 1,
        isMuted: false,
        isShuffled: false,
        isRepeated: false,
        isLiked: false,
        isSaved: false,
        playlist: [],
        currentIndex: 0,
        progressPercent: 0,
        
        // Initialize
        init() {
            this.syncWithGlobalState();
            this.setupMediaEventListeners();
        },
        
        syncWithGlobalState() {
            this.currentTrack = window.ahoyApp.currentTrack;
            this.isPlaying = window.ahoyApp.isPlaying;
            this.currentTime = window.ahoyApp.currentTime;
            this.volume = window.ahoyApp.volume;
            this.isMuted = window.ahoyApp.isMuted;
            this.isShuffled = window.ahoyApp.isShuffled;
            this.isRepeated = window.ahoyApp.isRepeated;
            this.isLiked = window.ahoyApp.isLiked;
            this.playlist = window.ahoyApp.playlist;
            this.currentIndex = window.ahoyApp.currentIndex;
            
            if (this.currentTrack && this.currentTrack.duration_seconds) {
                this.progressPercent = (this.currentTime / this.currentTrack.duration_seconds) * 100;
            }
        },
        
        setupMediaEventListeners() {
            // Listen for media events from the global media player
            document.addEventListener('play', (event) => {
                if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
                    this.isPlaying = true;
                    window.ahoyApp.isPlaying = true;
                }
            });
            
            document.addEventListener('pause', (event) => {
                if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
                    this.isPlaying = false;
                    window.ahoyApp.isPlaying = false;
                }
            });
            
            document.addEventListener('timeupdate', (event) => {
                if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
                    this.currentTime = event.target.currentTime;
                    window.ahoyApp.currentTime = event.target.currentTime;
                    
                    if (this.currentTrack && this.currentTrack.duration_seconds) {
                        this.progressPercent = (this.currentTime / this.currentTrack.duration_seconds) * 100;
                    }
                }
            });
            
            document.addEventListener('ended', (event) => {
                if (event.target.tagName === 'AUDIO' || event.target.tagName === 'VIDEO') {
                    this.isPlaying = false;
                    window.ahoyApp.isPlaying = false;
                    this.nextTrack();
                }
            });
        },
        
        // Player controls
        togglePlay() {
            if (window.globalPlayer) {
                if (this.isPlaying) {
                    window.globalPlayer.pauseTrack();
                } else {
                    window.globalPlayer.resumeTrack();
                }
            }
        },
        
        previousTrack() {
            if (window.globalPlayer) {
                window.globalPlayer.previousTrack();
            }
        },
        
        nextTrack() {
            if (window.globalPlayer) {
                window.globalPlayer.nextTrack();
            }
        },
        
        toggleShuffle() {
            this.isShuffled = !this.isShuffled;
            window.ahoyApp.isShuffled = this.isShuffled;
            
            if (this.isShuffled && this.playlist.length > 0) {
                this.shufflePlaylist();
            }
        },
        
        toggleRepeat() {
            this.isRepeated = !this.isRepeated;
            window.ahoyApp.isRepeated = this.isRepeated;
        },
        
        toggleMute() {
            this.isMuted = !this.isMuted;
            window.ahoyApp.isMuted = this.isMuted;
            
            const mediaElement = document.querySelector('#global-media-player');
            if (mediaElement) {
                mediaElement.muted = this.isMuted;
            }
        },
        
        toggleLike() {
            this.isLiked = !this.isLiked;
            window.ahoyApp.isLiked = this.isLiked;
            // TODO: Implement actual like functionality
        },
        
        toggleSave() {
            this.isSaved = !this.isSaved;
            window.ahoyApp.isSaved = this.isSaved;
            // TODO: Implement actual save functionality
            console.log('Save toggled:', this.isSaved, this.currentTrack);
        },
        
        addToPlaylist() {
            // TODO: Implement add to playlist functionality
            console.log('Add to playlist:', this.currentTrack);
        },
        
        openFullPlayer() {
            if (this.currentTrack) {
                const mediaType = this.currentTrack.type || 'music';
                window.location.href = `/player?id=${this.currentTrack.id}&type=${mediaType}`;
            }
        },
        
        seekTo(event) {
            if (!this.currentTrack) return;
            
            const progressBar = event.currentTarget;
            const rect = progressBar.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const percentage = clickX / rect.width;
            const newTime = percentage * (this.currentTrack.duration_seconds || 0);
            
            const mediaElement = document.querySelector('#global-media-player');
            if (mediaElement) {
                mediaElement.currentTime = newTime;
                this.currentTime = newTime;
                window.ahoyApp.currentTime = newTime;
            }
        },

        seekForward() {
            const mediaElement = document.querySelector('#global-media-player');
            if (mediaElement) {
                const newTime = Math.min(mediaElement.currentTime + 15, mediaElement.duration || 0);
                mediaElement.currentTime = newTime;
                this.currentTime = newTime;
                window.ahoyApp.currentTime = newTime;
            }
        },

        seekBackward() {
            const mediaElement = document.querySelector('#global-media-player');
            if (mediaElement) {
                const newTime = Math.max(mediaElement.currentTime - 15, 0);
                mediaElement.currentTime = newTime;
                this.currentTime = newTime;
                window.ahoyApp.currentTime = newTime;
            }
        },
        
        shufflePlaylist() {
            const playlist = [...this.playlist];
            for (let i = playlist.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [playlist[i], playlist[j]] = [playlist[j], playlist[i]];
            }
            this.playlist = playlist;
            window.ahoyApp.playlist = playlist;
        },
        
        // Utility functions
        formatTime(seconds) {
            if (!seconds || isNaN(seconds)) return '0:00';
            
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }
    };
}

// Simple fetch wrapper for new APIs
async function api(url, method="GET", payload=null) {
    const opts = { method, headers: { "Content-Type": "application/json" }, credentials: "include" };
    if (payload) opts.body = JSON.stringify(payload);
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(`API ${method} ${url} -> ${res.status}`);
    try { return await res.json(); } catch { return {}; }
}

// Event delegation for a single save mechanic: BOOKMARK with local storage fallback
document.addEventListener("click", async (e) => {
  // If any old templates still emit data-like, treat them as bookmarks too.
  const bmBtn = e.target.closest("[data-bookmark]") || e.target.closest("[data-like]");
  if (!bmBtn) return;

  e.preventDefault();
  const id = bmBtn.dataset.id;
  const kind = bmBtn.dataset.kind || "track";
  if (!id) return;

  try {
    bmBtn.classList.add("is-loading");
    
    // Try server first
    try {
      const { status } = await api("/api/activity/bookmark", "POST", { id, kind });
      bmBtn.classList.toggle("bookmarked", status === "bookmarked");
      if (status === "bookmarked") {
        window.__ahoyToast && window.__ahoyToast("Bookmarked!");
      }
    } catch (serverError) {
      // If server fails (not logged in), use local storage
      console.log("Server unavailable, using local storage");
      const key = `${kind}:${id}`;
      const localBookmarks = JSON.parse(localStorage.getItem('ahoy_bookmarks') || '[]');
      const isBookmarked = localBookmarks.includes(key);
      
      if (isBookmarked) {
        // Remove from local storage
        const newBookmarks = localBookmarks.filter(b => b !== key);
        localStorage.setItem('ahoy_bookmarks', JSON.stringify(newBookmarks));
        bmBtn.classList.remove("bookmarked");
        window.__ahoyToast && window.__ahoyToast("Removed from bookmarks");
      } else {
        // Add to local storage
        localBookmarks.push(key);
        localStorage.setItem('ahoy_bookmarks', JSON.stringify(localBookmarks));
        bmBtn.classList.add("bookmarked");
        window.__ahoyToast && window.__ahoyToast("Bookmarked! (Local - create account to sync)");
        
        // Show gentle account prompt after 3 bookmarks
        if (localBookmarks.length === 3) {
          setTimeout(() => {
            showAccountPrompt();
          }, 2000);
        }
      }
    }
  } catch (err) {
    console.error(err);
    window.__ahoyToast && window.__ahoyToast("Failed to bookmark");
  } finally {
    bmBtn.classList.remove("is-loading");
  }
});

// Account prompt function
function showAccountPrompt() {
  const prompt = document.createElement('div');
  prompt.className = 'account-prompt';
  prompt.innerHTML = `
    <div class="account-prompt-content">
      <div class="account-prompt-icon">🔖</div>
      <h3>Keep Your Bookmarks Forever!</h3>
      <p>You're saving content locally. Create a free account to sync your bookmarks across devices and never lose them.</p>
      <div class="account-prompt-actions">
        <button onclick="window.location.href='/register'" class="btn btn-primary">Create Account</button>
        <button onclick="this.closest('.account-prompt').remove()" class="btn btn-outline">Maybe Later</button>
      </div>
    </div>
  `;
  prompt.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--background-light, #fff);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    z-index: 1001;
    max-width: 400px;
    text-align: center;
    border: 1px solid #e5e7eb;
  `;
  document.body.appendChild(prompt);
  
  // Auto-remove after 15 seconds
  setTimeout(() => {
    if (prompt.parentNode) {
      prompt.remove();
    }
  }, 15000);
}

// Optional: hydrate bookmark state on page load (call from your page init if desired)
window.hydrateBookmarksState = async function hydrateBookmarksState() {
  try {
    // Try server first
    const me = await api("/api/activity/me", "GET");
    const set = new Set(me.bookmarks || []);
    document.querySelectorAll("[data-bookmark], [data-like]").forEach(btn => {
      const id = btn.dataset.id;
      const kind = btn.dataset.kind || "track";
      const key = `${kind}:${id}`;
      btn.classList.toggle("bookmarked", set.has(key));
    });
  } catch (e) {
    // If server fails, use local storage
    console.log("Server unavailable, using local storage for bookmarks");
    const localBookmarks = JSON.parse(localStorage.getItem('ahoy_bookmarks') || '[]');
    const set = new Set(localBookmarks);
    document.querySelectorAll("[data-bookmark], [data-like]").forEach(btn => {
      const id = btn.dataset.id;
      const kind = btn.dataset.kind || "track";
      const key = `${kind}:${id}`;
      btn.classList.toggle("bookmarked", set.has(key));
    });
  }
}

// Export functions for global use
window.ahoyApp = {
    ...window.ahoyApp,
    debounce,
    throttle,
    apiRequest,
    performSearch,
    showNotification,
    api
};

// Boot watchdog: clears the loading screen even if a request fails
(function boot() {
  function clearLoader() {
    const loader = document.getElementById("app-loader") || document.getElementById("loading-indicator");
    if (loader) loader.style.display = "none";
  }
  window.addEventListener("DOMContentLoaded", async () => {
    // try to hydrate bookmarks; even on failure, clear loader so UI is usable
    try { await window.hydrateBookmarksState(); } catch (e) { console.warn(e); }
    // If your app does additional bootstrapping, call it here in try/catch too.
    clearLoader();
  });

  // Safety net: if DOMContentLoaded didn't fire, force-clear loader after 5s
  setTimeout(clearLoader, 5000);
})();
