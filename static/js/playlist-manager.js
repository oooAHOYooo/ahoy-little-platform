// Ahoy Indie Media - Playlist Manager JavaScript

class PlaylistManager {
    constructor() {
        this.playlists = [];
        this.collections = [];
        this.likes = [];
        this.history = [];
        this.recommendations = [];
        this.userStats = {};
        
        this.initializeManager();
    }
    
    async initializeManager() {
        await this.loadUserData();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Listen for global events
        document.addEventListener('trackPlayed', (event) => {
            this.addToHistory(event.detail);
        });
        
        document.addEventListener('trackLiked', (event) => {
            this.toggleLike(event.detail);
        });
    }
    
    // User data management
    async loadUserData() {
        try {
            const [playlists, likes, history, recommendations, stats] = await Promise.all([
                this.fetchUserPlaylists(),
                this.fetchUserLikes(),
                this.fetchUserHistory(),
                this.fetchRecommendations(),
                this.fetchUserStats()
            ]);
            
            this.playlists = playlists;
            this.likes = likes;
            this.history = history;
            this.recommendations = recommendations;
            this.userStats = stats;
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }
    
    async fetchUserPlaylists() {
        try {
            const response = await fetch('/api/user/playlists');
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error('Error fetching playlists:', error);
            return [];
        }
    }
    
    async fetchUserLikes() {
        try {
            const response = await fetch('/api/user/likes');
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error('Error fetching likes:', error);
            return [];
        }
    }
    
    async fetchUserHistory() {
        try {
            const response = await fetch('/api/user/history');
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error('Error fetching history:', error);
            return [];
        }
    }
    
    async fetchRecommendations() {
        try {
            const response = await fetch('/api/user/recommendations');
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            return [];
        }
    }
    
    async fetchUserStats() {
        try {
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                const profile = await response.json();
                return profile.stats || {};
            }
            return {};
        } catch (error) {
            console.error('Error fetching user stats:', error);
            return {};
        }
    }
    
    // Playlist management
    async createPlaylist(playlistData) {
        try {
            const response = await fetch('/api/user/playlists', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(playlistData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.playlists.push(result.playlist);
                this.emit('playlistCreated', result.playlist);
                return result.playlist;
            }
            
            throw new Error('Failed to create playlist');
        } catch (error) {
            console.error('Error creating playlist:', error);
            throw error;
        }
    }
    
    async updatePlaylist(playlistId, updates) {
        try {
            const response = await fetch(`/api/user/playlists/${playlistId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            });
            
            if (response.ok) {
                const result = await response.json();
                const index = this.playlists.findIndex(p => p.id === playlistId);
                if (index !== -1) {
                    this.playlists[index] = result.playlist;
                    this.emit('playlistUpdated', result.playlist);
                }
                return result.playlist;
            }
            
            throw new Error('Failed to update playlist');
        } catch (error) {
            console.error('Error updating playlist:', error);
            throw error;
        }
    }
    
    async deletePlaylist(playlistId) {
        try {
            const response = await fetch(`/api/user/playlists/${playlistId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.playlists = this.playlists.filter(p => p.id !== playlistId);
                this.emit('playlistDeleted', playlistId);
                return true;
            }
            
            throw new Error('Failed to delete playlist');
        } catch (error) {
            console.error('Error deleting playlist:', error);
            throw error;
        }
    }
    
    async addToPlaylist(playlistId, item) {
        try {
            const response = await fetch(`/api/user/playlists/${playlistId}/items`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: item.id,
                    type: item.type || 'track'
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                const playlist = this.playlists.find(p => p.id === playlistId);
                if (playlist) {
                    playlist.items.push(result.item);
                    playlist.updated_at = new Date().toISOString();
                    this.emit('playlistItemAdded', { playlistId, item: result.item });
                }
                return result.item;
            }
            
            throw new Error('Failed to add item to playlist');
        } catch (error) {
            console.error('Error adding to playlist:', error);
            throw error;
        }
    }
    
    async removeFromPlaylist(playlistId, item) {
        try {
            const response = await fetch(`/api/user/playlists/${playlistId}/items`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: item.id,
                    type: item.type || 'track'
                })
            });
            
            if (response.ok) {
                const playlist = this.playlists.find(p => p.id === playlistId);
                if (playlist) {
                    playlist.items = playlist.items.filter(i => 
                        !(i.id === item.id && i.type === item.type)
                    );
                    playlist.updated_at = new Date().toISOString();
                    this.emit('playlistItemRemoved', { playlistId, item });
                }
                return true;
            }
            
            throw new Error('Failed to remove item from playlist');
        } catch (error) {
            console.error('Error removing from playlist:', error);
            throw error;
        }
    }
    
    async reorderPlaylist(playlistId, newOrder) {
        try {
            const response = await fetch(`/api/user/playlists/${playlistId}/reorder`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ order: newOrder })
            });
            
            if (response.ok) {
                const result = await response.json();
                const playlist = this.playlists.find(p => p.id === playlistId);
                if (playlist) {
                    playlist.items = result.playlist.items;
                    playlist.updated_at = result.playlist.updated_at;
                    this.emit('playlistReordered', { playlistId, items: playlist.items });
                }
                return result.playlist;
            }
            
            throw new Error('Failed to reorder playlist');
        } catch (error) {
            console.error('Error reordering playlist:', error);
            throw error;
        }
    }
    
    // Like management
    async toggleLike(item) {
        try {
            const isLiked = this.isLiked(item);
            
            const response = await fetch('/api/user/likes', {
                method: isLiked ? 'DELETE' : 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: item.id,
                    type: item.type || 'track'
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.liked) {
                    this.likes.push({
                        id: item.id,
                        type: item.type || 'track',
                        liked_at: new Date().toISOString()
                    });
                } else {
                    this.likes = this.likes.filter(like => 
                        !(like.id === item.id && like.type === item.type)
                    );
                }
                
                this.emit('likeToggled', { item, liked: result.liked });
                return result.liked;
            }
            
            throw new Error('Failed to toggle like');
        } catch (error) {
            console.error('Error toggling like:', error);
            throw error;
        }
    }
    
    isLiked(item) {
        return this.likes.some(like => 
            like.id === item.id && like.type === (item.type || 'track')
        );
    }
    
    // History management
    async addToHistory(item) {
        try {
            const response = await fetch('/api/user/history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: item.id,
                    type: item.type || 'track',
                    duration_played: item.duration_played || 0
                })
            });
            
            if (response.ok) {
                const historyItem = {
                    id: item.id,
                    type: item.type || 'track',
                    played_at: new Date().toISOString(),
                    duration_played: item.duration_played || 0
                };
                
                this.history.unshift(historyItem);
                this.history = this.history.slice(0, 100); // Keep only last 100 items
                
                this.emit('historyUpdated', historyItem);
                return historyItem;
            }
            
            throw new Error('Failed to add to history');
        } catch (error) {
            console.error('Error adding to history:', error);
            throw error;
        }
    }
    
    // Collection management
    async createCollection(collectionData) {
        try {
            const response = await fetch('/api/user/collections', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(collectionData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.collections.push(result.collection);
                this.emit('collectionCreated', result.collection);
                return result.collection;
            }
            
            throw new Error('Failed to create collection');
        } catch (error) {
            console.error('Error creating collection:', error);
            throw error;
        }
    }
    
    // Search and filtering
    searchPlaylists(query) {
        if (!query) return this.playlists;
        
        const searchTerm = query.toLowerCase();
        return this.playlists.filter(playlist => 
            playlist.name.toLowerCase().includes(searchTerm) ||
            playlist.description?.toLowerCase().includes(searchTerm) ||
            playlist.tags?.some(tag => tag.toLowerCase().includes(searchTerm))
        );
    }
    
    getPlaylistsByTag(tag) {
        return this.playlists.filter(playlist => 
            playlist.tags?.includes(tag)
        );
    }
    
    getPublicPlaylists() {
        return this.playlists.filter(playlist => playlist.is_public);
    }
    
    getRecentPlaylists(limit = 10) {
        return this.playlists
            .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
            .slice(0, limit);
    }
    
    // Statistics
    getPlaylistStats() {
        const totalPlaylists = this.playlists.length;
        const publicPlaylists = this.playlists.filter(p => p.is_public).length;
        const totalItems = this.playlists.reduce((sum, playlist) => sum + playlist.items.length, 0);
        const totalLikes = this.likes.length;
        const totalHistory = this.history.length;
        
        return {
            totalPlaylists,
            publicPlaylists,
            privatePlaylists: totalPlaylists - publicPlaylists,
            totalItems,
            totalLikes,
            totalHistory,
            averageItemsPerPlaylist: totalPlaylists > 0 ? Math.round(totalItems / totalPlaylists) : 0
        };
    }
    
    // Utility functions
    getPlaylistCover(playlist) {
        if (playlist.items && playlist.items.length > 0) {
            const firstItem = playlist.items[0];
            return firstItem.cover_art || firstItem.thumbnail || '/static/img/default-cover.jpg';
        }
        return '/static/img/default-playlist-cover.jpg';
    }
    
    getPlaylistDuration(playlist) {
        if (!playlist || !playlist.items) return 0;
        return playlist.items.reduce((total, item) => total + (item.duration_seconds || 0), 0);
    }
    
    formatDuration(seconds) {
        if (!seconds) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }
    
    // Event system
    emit(event, data) {
        document.dispatchEvent(new CustomEvent(event, { detail: data }));
    }
    
    on(event, callback) {
        document.addEventListener(event, callback);
    }
    
    off(event, callback) {
        document.removeEventListener(event, callback);
    }
}

// Create global playlist manager instance
window.playlistManager = new PlaylistManager();

// Alpine.js data for playlist components
window.playlistManagerData = function() {
    return {
        // State
        playlists: [],
        collections: [],
        likes: [],
        history: [],
        recommendations: [],
        userStats: {},
        
        // UI state
        currentView: 'overview',
        playlistView: 'grid',
        likedFilter: 'all',
        showCreatePlaylist: false,
        showCreateCollection: false,
        selectedPlaylist: null,
        selectedItem: null,
        searchQuery: '',
        
        // Form data
        newPlaylist: {
            name: '',
            description: '',
            is_public: false,
            tags: ''
        },
        
        newCollection: {
            name: '',
            description: '',
            type: 'mixed',
            tags: ''
        },
        
        // Initialize
        async init() {
            await this.loadUserData();
            this.setupEventListeners();
        },
        
        async loadUserData() {
            this.playlists = window.playlistManager.playlists;
            this.collections = window.playlistManager.collections;
            this.likes = window.playlistManager.likes;
            this.history = window.playlistManager.history;
            this.recommendations = window.playlistManager.recommendations;
            this.userStats = window.playlistManager.userStats;
        },
        
        setupEventListeners() {
            // Listen to playlist manager events
            window.playlistManager.on('playlistCreated', (playlist) => {
                this.playlists.push(playlist);
            });
            
            window.playlistManager.on('playlistUpdated', (playlist) => {
                const index = this.playlists.findIndex(p => p.id === playlist.id);
                if (index !== -1) {
                    this.playlists[index] = playlist;
                }
            });
            
            window.playlistManager.on('playlistDeleted', (playlistId) => {
                this.playlists = this.playlists.filter(p => p.id !== playlistId);
            });
            
            window.playlistManager.on('likeToggled', (data) => {
                this.likes = window.playlistManager.likes;
            });
            
            window.playlistManager.on('historyUpdated', (item) => {
                this.history = window.playlistManager.history;
            });
        },
        
        // Playlist management
        async createPlaylist() {
            try {
                const tags = this.newPlaylist.tags ? 
                    this.newPlaylist.tags.split(',').map(t => t.trim()) : [];
                
                const playlist = await window.playlistManager.createPlaylist({
                    ...this.newPlaylist,
                    tags
                });
                
                this.showCreatePlaylist = false;
                this.resetNewPlaylistForm();
                return playlist;
            } catch (error) {
                console.error('Error creating playlist:', error);
                window.ahoyApp.showNotification('Failed to create playlist', 'error');
            }
        },
        
        resetNewPlaylistForm() {
            this.newPlaylist = {
                name: '',
                description: '',
                is_public: false,
                tags: ''
            };
        },
        
        async updatePlaylist(playlistId, updates) {
            try {
                await window.playlistManager.updatePlaylist(playlistId, updates);
            } catch (error) {
                console.error('Error updating playlist:', error);
                window.ahoyApp.showNotification('Failed to update playlist', 'error');
            }
        },
        
        async deletePlaylist(playlistId) {
            if (confirm('Are you sure you want to delete this playlist?')) {
                try {
                    await window.playlistManager.deletePlaylist(playlistId);
                    window.ahoyApp.showNotification('Playlist deleted', 'success');
                } catch (error) {
                    console.error('Error deleting playlist:', error);
                    window.ahoyApp.showNotification('Failed to delete playlist', 'error');
                }
            }
        },
        
        async addToPlaylist(item, playlistId) {
            try {
                await window.playlistManager.addToPlaylist(playlistId, item);
                window.ahoyApp.showNotification('Added to playlist', 'success');
            } catch (error) {
                console.error('Error adding to playlist:', error);
                window.ahoyApp.showNotification('Failed to add to playlist', 'error');
            }
        },
        
        async removeFromPlaylist(playlistId, item) {
            try {
                await window.playlistManager.removeFromPlaylist(playlistId, item);
                window.ahoyApp.showNotification('Removed from playlist', 'success');
            } catch (error) {
                console.error('Error removing from playlist:', error);
                window.ahoyApp.showNotification('Failed to remove from playlist', 'error');
            }
        },
        
        // Like management
        async toggleLike(item) {
            try {
                await window.playlistManager.toggleLike(item);
            } catch (error) {
                console.error('Error toggling like:', error);
                window.ahoyApp.showNotification('Failed to update like', 'error');
            }
        },
        
        isLiked(item) {
            return window.playlistManager.isLiked(item);
        },
        
        // Utility functions
        getPlaylistCover(playlist) {
            return window.playlistManager.getPlaylistCover(playlist);
        },
        
        getPlaylistDuration(playlist) {
            return window.playlistManager.getPlaylistDuration(playlist);
        },
        
        formatDuration(seconds) {
            return window.playlistManager.formatDuration(seconds);
        },
        
        formatDate(dateString) {
            return window.playlistManager.formatDate(dateString);
        },
        
        getFilteredLikes() {
            if (this.likedFilter === 'all') return this.likes;
            return this.likes.filter(like => like.type === this.likedFilter);
        },
        
        getPlaylistItems(playlist) {
            return playlist?.items || [];
        },
        
        // Search
        searchPlaylists() {
            return window.playlistManager.searchPlaylists(this.searchQuery);
        }
    };
};

// Export for global use
window.PlaylistManager = PlaylistManager;
