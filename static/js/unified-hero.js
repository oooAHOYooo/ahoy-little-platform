/**
 * Unified Hero System - Reusable carousel functionality for subpages
 * Keeps homepage separate with its own tv-hero system
 */

function createUnifiedHero(config = {}) {
    return {
        // Configuration
        pageType: config.pageType || 'music',
        heroItems: [],
        currentHeroIndex: 0,
        heroOffset: 0,
        heroInterval: null,
        rotationSpeed: config.rotationSpeed || 6000, // 6 seconds
        searchQuery: '',
        isLoading: true,
        
        // Touch handling
        touchStartX: 0,
        touchStartY: 0,
        isDragging: false,
        
        // Initialize
        async init() {
            await this.loadHeroContent();
            this.startHeroRotation();
            this.setupEventListeners();
            this.isLoading = false;
        },
        
        // Load content based on page type
        async loadHeroContent() {
            try {
                let endpoint = '';
                switch (this.pageType) {
                    case 'music':
                        endpoint = '/api/music';
                        break;
                    case 'shows':
                        endpoint = '/api/shows';
                        break;
                    case 'artists':
                        endpoint = '/api/artists';
                        break;
                    case 'saves':
                        endpoint = '/api/saves/featured';
                        break;
                    case 'account':
                        endpoint = '/api/user/featured';
                        break;
                    default:
                        endpoint = '/api/music';
                }
                
                const response = await fetch(endpoint);
                const data = await response.json();
                
                // Extract items based on page type
                let items = [];
                switch (this.pageType) {
                    case 'music':
                        items = (data.tracks || []).slice(0, 6);
                        break;
                    case 'shows':
                        items = (data.shows || []).slice(0, 6);
                        break;
                    case 'artists':
                        items = (data.artists || []).slice(0, 6);
                        break;
                    case 'saves':
                        items = (data.content || []).slice(0, 6);
                        break;
                    case 'account':
                        items = (data.featured || []).slice(0, 6);
                        break;
                }
                
                // Shuffle for variety
                this.heroItems = items.sort(() => 0.5 - Math.random());
                
                // Set initial offset
                this.$nextTick(() => {
                    this.updateHeroOffset();
                });
                
            } catch (error) {
                console.error('Error loading hero content:', error);
                this.heroItems = this.getFallbackItems();
            }
        },
        
        // Fallback items if API fails
        getFallbackItems() {
            const fallbacks = {
                music: [
                    {
                        id: 'fallback-1',
                        title: 'Discover Music',
                        artist: 'Independent Artists',
                        cover_art: '/static/img/default-cover.jpg',
                        type: 'music'
                    }
                ],
                shows: [
                    {
                        id: 'fallback-1',
                        title: 'Watch Shows',
                        host: 'Ahoy Indie Media',
                        thumbnail: '/static/img/default-cover.jpg',
                        type: 'show'
                    }
                ],
                artists: [
                    {
                        id: 'fallback-1',
                        name: 'Discover Artists',
                        description: 'Independent Creators',
                        image: '/static/img/default-avatar.png',
                        type: 'artist'
                    }
                ],
                saves: [
                    {
                        id: 'fallback-1',
                        title: 'Your Saves',
                        description: 'Saved content appears here',
                        cover_art: '/static/img/default-cover.jpg',
                        type: 'save'
                    }
                ],
                account: [
                    {
                        id: 'fallback-1',
                        title: 'Your Account',
                        description: 'Manage your profile',
                        cover_art: '/static/img/default-avatar.png',
                        type: 'account'
                    }
                ]
            };
            
            return fallbacks[this.pageType] || fallbacks.music;
        },
        
        // Hero rotation
        startHeroRotation() {
            if (this.heroItems.length <= 1) return;
            
            this.heroInterval = setInterval(() => {
                if (!this.isDragging) {
                    this.nextHero();
                }
            }, this.rotationSpeed);
        },
        
        stopHeroRotation() {
            if (this.heroInterval) {
                clearInterval(this.heroInterval);
                this.heroInterval = null;
            }
        },
        
        // Navigation
        nextHero() {
            if (this.heroItems.length === 0) return;
            
            if (this.currentHeroIndex < this.heroItems.length - 1) {
                this.currentHeroIndex++;
            } else {
                this.currentHeroIndex = 0;
            }
            this.updateHeroOffset();
        },
        
        prevHero() {
            if (this.heroItems.length === 0) return;
            
            if (this.currentHeroIndex > 0) {
                this.currentHeroIndex--;
            } else {
                this.currentHeroIndex = this.heroItems.length - 1;
            }
            this.updateHeroOffset();
        },
        
        setHeroIndex(index) {
            this.currentHeroIndex = index;
            this.updateHeroOffset();
            this.stopHeroRotation();
            setTimeout(() => this.startHeroRotation(), 3000);
        },
        
        updateHeroOffset() {
            const heroFeed = document.querySelector('.unified-hero-feed');
            if (heroFeed) {
                const containerWidth = heroFeed.parentElement.offsetWidth;
                this.heroOffset = -this.currentHeroIndex * containerWidth;
            }
        },
        
        // Touch handling
        handleTouchStart(event) {
            this.touchStartX = event.touches[0].clientX;
            this.touchStartY = event.touches[0].clientY;
            this.isDragging = false;
            this.stopHeroRotation();
        },
        
        handleTouchMove(event) {
            if (!this.touchStartX) return;

            const touchX = event.touches[0].clientX;
            const touchY = event.touches[0].clientY;
            const diffX = this.touchStartX - touchX;
            const diffY = this.touchStartY - touchY;

            // Only hijack scroll after significant horizontal movement (10px threshold)
            // This allows vertical scrolling to work normally
            const minThreshold = 10;
            if (Math.abs(diffX) > minThreshold && Math.abs(diffX) > Math.abs(diffY) * 1.5) {
                this.isDragging = true;
                // Only prevent default if clearly a horizontal swipe
                event.preventDefault();
            }
        },
        
        handleTouchEnd(event) {
            if (!this.isDragging || !this.touchStartX) {
                this.startHeroRotation();
                return;
            }
            
            const touchX = event.changedTouches[0].clientX;
            const diffX = this.touchStartX - touchX;
            const threshold = 50;
            
            if (Math.abs(diffX) > threshold) {
                if (diffX > 0) {
                    this.nextHero();
                } else {
                    this.prevHero();
                }
            }
            
            this.touchStartX = 0;
            this.touchStartY = 0;
            this.isDragging = false;
            setTimeout(() => this.startHeroRotation(), 3000);
        },
        
        // Search functionality
        performSearch() {
            if (!this.searchQuery.trim()) return;
            
            const searchUrl = `/search?q=${encodeURIComponent(this.searchQuery)}&type=${this.pageType}`;
            window.location.href = searchUrl;
        },
        
        clearSearch() {
            this.searchQuery = '';
        },
        
        // Content actions
        playHeroItem(item) {
            this.stopHeroRotation();
            
            const tryPlayMusic = (track) => {
                if (!track) return false;
                // Prefer direct playback if possible
                if (window.mediaPlayer && typeof window.mediaPlayer.play === 'function') {
                    window.mediaPlayer.play(track);
                    return true;
                }
                if (window.PlayerControls && typeof window.PlayerControls.play === 'function') {
                    window.PlayerControls.play(track);
                    return true;
                }
                if (window.globalPlayer && typeof window.globalPlayer.playTrack === 'function') {
                    window.globalPlayer.playTrack(track);
                    return true;
                }
                return false;
            };
            
            switch (this.pageType) {
                case 'music': {
                    const played = tryPlayMusic(item);
                    if (!played) {
                        window.location.href = `/player?id=${item.id}&type=music`;
                    }
                    break;
                }
                case 'shows': {
                    // Prefer dedicated player page for shows (video UX)
                    window.location.href = `/player?id=${item.id}&type=show`;
                    break;
                }
                case 'artists': {
                    const artistSlug = item.name.toLowerCase()
                        .replace(/\s+/g, '-')
                        .replace(/[^a-z0-9-]/g, '');
                    window.location.href = `/artist/${artistSlug}`;
                    break;
                }
                case 'saves':
                case 'account': {
                    if (item.type === 'music') {
                        const played = tryPlayMusic(item);
                        if (!played) {
                            window.location.href = `/player?id=${item.id}&type=music`;
                        }
                    } else if (item.type === 'show') {
                        window.location.href = `/player?id=${item.id}&type=show`;
                    }
                    break;
                }
            }
            
            setTimeout(() => this.startHeroRotation(), 10000);
        },
        
        // Utility functions
        getItemImage(item) {
            switch (this.pageType) {
                case 'music':
                    return item.cover_art || '/static/img/default-cover.jpg';
                case 'shows':
                    return item.thumbnail || '/static/img/default-cover.jpg';
                case 'artists':
                    return item.image || '/static/img/default-avatar.png';
                case 'saves':
                case 'account':
                    return item.cover_art || item.thumbnail || item.image || '/static/img/default-cover.jpg';
                default:
                    return '/static/img/default-cover.jpg';
            }
        },
        
        getItemTitle(item) {
            switch (this.pageType) {
                case 'artists':
                    return item.name || 'Unknown Artist';
                default:
                    return item.title || 'Unknown Title';
            }
        },
        
        getItemSubtitle(item) {
            switch (this.pageType) {
                case 'music':
                    return item.artist || 'Unknown Artist';
                case 'shows':
                    return item.host || 'Unknown Host';
                case 'artists':
                    return item.description || item.genre || 'Artist';
                case 'saves':
                case 'account':
                    return item.artist || item.host || item.description || '';
                default:
                    return '';
            }
        },
        
        getPageBadge() {
            const badges = {
                music: 'MUSIC',
                shows: 'SHOWS',
                artists: 'ARTISTS',
                saves: 'MY SAVES',
                account: 'ACCOUNT'
            };
            return badges[this.pageType] || 'CONTENT';
        },
        
        getPageTitle() {
            const titles = {
                music: 'Music Library',
                shows: 'Videos',
                videos: 'Videos',
                artists: 'Artists',
                saves: 'My Saves',
                account: 'My Account'
            };
            return titles[this.pageType] || 'Content';
        },
        
        getPageDescription() {
            const descriptions = {
                music: 'Discover tracks, albums, and artists',
                shows: 'Music videos, skate parts, short films, episodes, and more',
                videos: 'Music videos, skate parts, short films, episodes, and more',
                artists: 'Discover indie musicians, show hosts, athletes, filmmakers, and more',
                saves: 'Your saved tracks, videos, playlists, and more',
                account: 'Manage your profile and preferences'
            };
            return descriptions[this.pageType] || 'Discover content';
        },
        
        getSearchPlaceholder() {
            const placeholders = {
                music: 'Search music, artists, or genres...',
                shows: 'Search shows, hosts, or descriptions...',
                artists: 'Search artists, genres, or descriptions...',
                saves: 'Search your saves...',
                account: 'Search your content...'
            };
            return placeholders[this.pageType] || 'Search...';
        },
        
        // Event listeners
        setupEventListeners() {
            window.addEventListener('resize', () => {
                this.updateHeroOffset();
            });
            
            // Pause rotation on focus/hover
            const heroElement = document.querySelector('.unified-hero');
            if (heroElement) {
                heroElement.addEventListener('mouseenter', () => {
                    this.stopHeroRotation();
                });
                
                heroElement.addEventListener('mouseleave', () => {
                    setTimeout(() => this.startHeroRotation(), 1000);
                });
            }
        },
        
        // Cleanup
        destroy() {
            this.stopHeroRotation();
            window.removeEventListener('resize', this.updateHeroOffset);
        }
    };
}

// Export for global use
window.createUnifiedHero = createUnifiedHero;

