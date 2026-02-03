import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ahoy.app',
  appName: 'Ahoy Indie Media',
  webDir: 'static',
  server: {
    url: 'http://10.0.2.2:5001',
    cleartext: true
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
