/**
 * Cross-platform storage helper for Ahoy Indie Media
 * Uses Capacitor Preferences on mobile, falls back to localStorage on web
 */
(function() {
  'use strict';

  let storageImpl = null;
  let isCapacitor = false;

  // Detect Capacitor environment
  if (typeof window !== 'undefined' && window.Capacitor) {
    try {
      // Capacitor 5 plugin access
      const { Preferences } = window.Capacitor.Plugins || {};
      if (Preferences && typeof Preferences.get === 'function') {
        storageImpl = Preferences;
        isCapacitor = true;
      } else {
        // Try alternative import for Capacitor 5
        const Capacitor = window.Capacitor;
        if (Capacitor && Capacitor.Plugins && Capacitor.Plugins.Preferences) {
          storageImpl = Capacitor.Plugins.Preferences;
          isCapacitor = true;
        }
      }
    } catch (e) {
      console.warn('Capacitor Preferences not available, using localStorage fallback', e);
    }
  }

  // Fallback to localStorage
  if (!storageImpl) {
    storageImpl = {
      async get(options) {
        try {
          const value = localStorage.getItem(options.key);
          return { value: value !== null ? value : undefined };
        } catch (e) {
          console.error('localStorage.get error:', e);
          return { value: undefined };
        }
      },
      async set(options) {
        try {
          localStorage.setItem(options.key, String(options.value));
        } catch (e) {
          console.error('localStorage.set error:', e);
          // Handle quota exceeded
          if (e.name === 'QuotaExceededError') {
            console.warn('Storage quota exceeded, clearing old data');
            // Clear old data (keep only recent bookmarks)
            try {
              const keys = Object.keys(localStorage);
              keys.forEach(key => {
                if (key.startsWith('ahoy.') && !key.includes('bookmarks.v1')) {
                  localStorage.removeItem(key);
                }
              });
              // Try again
              localStorage.setItem(options.key, String(options.value));
            } catch (e2) {
              console.error('Failed to clear storage:', e2);
            }
          }
        }
      },
      async remove(options) {
        try {
          localStorage.removeItem(options.key);
        } catch (e) {
          console.error('localStorage.remove error:', e);
        }
      },
      async keys() {
        try {
          return { keys: Object.keys(localStorage) };
        } catch (e) {
          console.error('localStorage.keys error:', e);
          return { keys: [] };
        }
      },
      async clear() {
        try {
          localStorage.clear();
        } catch (e) {
          console.error('localStorage.clear error:', e);
        }
      }
    };
  }

  /**
   * Storage API compatible with both Capacitor and localStorage
   */
  window.AhoyStorage = {
    /**
     * Get a value from storage
     * @param {string} key - Storage key
     * @returns {Promise<string|null>} - Stored value or null
     */
    async getItem(key) {
      try {
        const result = await storageImpl.get({ key });
        return result.value !== undefined ? result.value : null;
      } catch (e) {
        console.error('Storage.getItem error:', e);
        return null;
      }
    },

    /**
     * Set a value in storage
     * @param {string} key - Storage key
     * @param {string} value - Value to store
     * @returns {Promise<void>}
     */
    async setItem(key, value) {
      try {
        await storageImpl.set({ key, value: String(value) });
      } catch (e) {
        console.error('Storage.setItem error:', e);
        throw e;
      }
    },

    /**
     * Remove a value from storage
     * @param {string} key - Storage key
     * @returns {Promise<void>}
     */
    async removeItem(key) {
      try {
        await storageImpl.remove({ key });
      } catch (e) {
        console.error('Storage.removeItem error:', e);
      }
    },

    /**
     * Get all keys in storage
     * @returns {Promise<string[]>}
     */
    async keys() {
      try {
        const result = await storageImpl.keys();
        return result.keys || [];
      } catch (e) {
        console.error('Storage.keys error:', e);
        return [];
      }
    },

    /**
     * Clear all storage
     * @returns {Promise<void>}
     */
    async clear() {
      try {
        await storageImpl.clear();
      } catch (e) {
        console.error('Storage.clear error:', e);
      }
    },

    /**
     * Check if Capacitor storage is being used
     * @returns {boolean}
     */
    isCapacitor() {
      return isCapacitor;
    }
  };

  // Also provide synchronous localStorage-like API for backward compatibility
  // This will use async storage but provide sync interface for non-critical operations
  if (!isCapacitor) {
    // On web, we can provide sync access
    window.AhoyStorageSync = {
      getItem(key) {
        try {
          return localStorage.getItem(key);
        } catch (e) {
          return null;
        }
      },
      setItem(key, value) {
        try {
          localStorage.setItem(key, String(value));
        } catch (e) {
          console.error('localStorage.setItem error:', e);
        }
      },
      removeItem(key) {
        try {
          localStorage.removeItem(key);
        } catch (e) {
          console.error('localStorage.removeItem error:', e);
        }
      }
    };
  } else {
    // On mobile, sync operations are not available
    // Create a cache for frequently accessed items
    const syncCache = new Map();
    window.AhoyStorageSync = {
      getItem(key) {
        // Return from cache if available
        if (syncCache.has(key)) {
          return syncCache.get(key);
        }
        // For mobile, sync access is limited - return null and let async handle it
        return null;
      },
      setItem(key, value) {
        // Update cache
        syncCache.set(key, String(value));
        // Async update in background
        window.AhoyStorage.setItem(key, value).catch(e => {
          console.error('Background storage update failed:', e);
        });
      },
      removeItem(key) {
        syncCache.delete(key);
        window.AhoyStorage.removeItem(key).catch(e => {
          console.error('Background storage remove failed:', e);
        });
      }
    };
  }

  console.log('AhoyStorage initialized', { isCapacitor, hasStorage: !!storageImpl });
})();
