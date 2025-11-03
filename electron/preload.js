/**
 * Preload script for Electron security
 * Exposes safe APIs to the renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getVersion: () => ipcRenderer.invoke('get-version'),
  
  // Server status
  onServerError: (callback) => {
    ipcRenderer.on('server-error', (event, error) => callback(error));
  },
  
  // Platform info
  platform: process.platform,
  isElectron: true,
});

// Log that preload script loaded
console.log('Electron preload script loaded');

