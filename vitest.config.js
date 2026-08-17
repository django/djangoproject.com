import { defineConfig } from 'vitest/config';
import { webdriverio } from '@vitest/browser-webdriverio';

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      headless: false, // Safari doesn't support it yet :(
      provider: webdriverio(),
      // https://vitest.dev/config/browser/webdriverio
      instances: [
        { browser: 'chrome' },
        { browser: 'firefox' },
        { browser: 'safari' },
      ],
    },
    coverage: {
      enabled: true,
      provider: 'istanbul',
    },
  },
});
