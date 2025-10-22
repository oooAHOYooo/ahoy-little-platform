import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ahoy.app',
  appName: 'Ahoy Indie Media',
  webDir: 'static',
  server: {
    url: 'https://ahoy-indie-media.onrender.com',
    cleartext: false
  },
  android: {
    allowMixedContent: false
  },
  plugins: {
    SplashScreen: {
      launchAutoHide: true
    }
  }
};

export default config;
