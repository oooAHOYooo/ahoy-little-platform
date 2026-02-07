import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ahoy.app',
  appName: 'Ahoy Indie Media',
  webDir: 'static',
  server: {
    url: 'https://app.ahoy.ooo',
    cleartext: false
  },
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
