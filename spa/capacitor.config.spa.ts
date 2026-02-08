/**
 * Capacitor config for SPA mode (v2).
 *
 * Instead of loading from a remote URL, the app loads from the
 * built SPA files in spa-dist/. The SPA fetches data from the
 * API server at https://app.ahoy.ooo/api/*.
 *
 * To use this config:
 *   1. cd spa && npm run build    (outputs to ../spa-dist)
 *   2. Copy this file to ../capacitor.config.ts (replacing the remote-URL version)
 *   3. npx cap sync android && npx cap sync ios
 *   4. Build in Android Studio / Xcode
 */
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ahoy.app',
  appName: 'Ahoy Indie Media',
  webDir: 'spa-dist',
  // No server.url — loads from local files (the SPA build output)
  android: {
    allowMixedContent: false
  },
  ios: {
    contentInset: 'automatic',
    allowsLinkPreview: false,
    scrollEnabled: true
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: true,
      launchShowDuration: 2000
    }
  }
};

export default config;
