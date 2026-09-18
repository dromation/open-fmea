const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests', timeout: 30000, workers: 1,
  reporter: [['list'], ['json', { outputFile: 'verification/browser-tests.json' }]],
  use: { baseURL: 'http://127.0.0.1:4178', channel: 'chrome',
    viewport: { width: 1600, height: 1100 }, screenshot: 'only-on-failure' },
  webServer: { command: 'node tools/serve-preview.cjs', url: 'http://127.0.0.1:4178', reuseExistingServer: false }
});
