import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ahoy.app',
  appName: 'Ahoy Indie Media',
  webDir: 'spa-dist',
  // No server.url — loads the Vue SPA from local built files.
  // The SPA fetches data from https://app.ahoy.ooo/api/* at runtime.
  android: {
    allowMixedContent: false,
  },
  ios: {
    contentInset: 'automatic',
    allowsLinkPreview: false,
    scrollEnabled: true,
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: true,
      launchShowDuration: 2000,
    },
  },
};

export default config;
