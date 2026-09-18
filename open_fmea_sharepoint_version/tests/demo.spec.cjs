const { test, expect } = require('@playwright/test');
const fs = require('node:fs');

async function open(page, suffix = '') {
  await page.goto('/' + suffix);
  const ui = page.frameLocator('iframe');
  await expect(ui.locator('.navbtn[data-page="home"]')).toBeVisible();
  return { ui, frame: await (await page.locator('iframe').elementHandle()).contentFrame() };
}

test('all existing navigation renders inside an isolated frame', async ({ page }) => {
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const { ui, frame } = await open(page);
  const ids = await ui.locator('.navbtn[data-page]').evaluateAll(nodes => nodes.map(n => n.dataset.page));
  for (const id of ids) {
    await ui.locator(`.navbtn[data-page="${id}"]`).click();
    await expect(ui.locator('#page .errorbox')).toHaveCount(0);
    await expect(ui.locator('#page')).not.toBeEmpty();
  }
  expect(await frame.evaluate(() => {
    try { return Boolean(parent.document); } catch { return false; }
  })).toBe(false);
  expect(errors).toEqual([]);
  await ui.locator('.navbtn[data-page="dfmea"]').click();
  await ui.locator('.sidebar').evaluate(element => { element.scrollTop = 0; });
  fs.mkdirSync('verification', { recursive: true });
  await page.screenshot({ path: 'verification/sharepoint-demo-preview.png', fullPage: true });
});

test('DFMEA edits survive reload and are isolated between web part instances', async ({ page }) => {
  let { ui, frame } = await open(page);
  await ui.locator('.navbtn[data-page="dfmea"]').click();
  await frame.evaluate(() => window.OpenFMEA.Commands.createDFMEA());
  for (const [field, text] of Object.entries({element: 'SP test assembly', function: 'Provide light',
    failure: 'SP persistence test', effect: 'No light', cause: 'Open circuit'})) {
    await ui.locator('#ed_' + field).fill(text);
  }
  await ui.getByRole('button', { name: 'Save Item', exact: true }).click();
  await expect(page.getByRole('status')).toContainText('Saved in this browser');
  await page.reload();
  await expect(page.frameLocator('iframe').locator('.navbtn[data-page="home"]')).toBeVisible();
  frame = await (await page.locator('iframe').elementHandle()).contentFrame();
  expect(await frame.evaluate(() => window.OFMEA.C.dfmea.some(r => r.failure === 'SP persistence test'))).toBe(true);
  ({ frame } = await open(page, '?instance=second'));
  expect(await frame.evaluate(() => window.OFMEA.C.dfmea.some(r => r.failure === 'SP persistence test'))).toBe(false);
  ({ frame } = await open(page));
  await frame.evaluate(() => {
    const config = window.__openFmeaHostConfig;
    parent.postMessage({channel: 'open-fmea-demo-v1', token: config.token, operation: 'reset'}, config.origin);
  });
  await expect(page.getByRole('status')).toContainText('Embedded demo data');
  await expect(page.frameLocator('iframe').locator('.navbtn[data-page="home"]')).toBeVisible();
  frame = await (await page.locator('iframe').elementHandle()).contentFrame();
  expect(await frame.evaluate(() => window.OFMEA.C.dfmea.some(r => r.failure === 'SP persistence test'))).toBe(false);
});

test('portable container export works from the sandbox', async ({ page }) => {
  const { frame } = await open(page);
  const downloadEvent = page.waitForEvent('download');
  await frame.evaluate(() => window.OFMEA.saveContainer());
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toBe('open_fmea.container');
  const json = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
  expect(json.projects.length).toBe(7);
  expect(json.dfmea.length).toBe(11);
});

test('confirmation dialogs remain usable', async ({ page }) => {
  const { frame } = await open(page);
  let shown = false;
  page.once('dialog', async dialog => { shown = true; await dialog.accept(); });
  const accepted = await frame.evaluate(() => window.confirm('Confirm dialog smoke test'));
  expect(shown).toBe(true);
  expect(accepted).toBe(true);
});

test('storage failure is visible and does not claim successful persistence', async ({ page }) => {
  await page.addInitScript(() => {
    Storage.prototype.setItem = () => { throw new DOMException('Test quota exceeded', 'QuotaExceededError'); };
  });
  const { ui, frame } = await open(page);
  await frame.evaluate(() => document.querySelector('[data-page="dfmea"]').click());
  await frame.evaluate(() => { window.OFMEA.C.settings.test = true; window.OFMEA.Runtime.Commands.completeAction('ACT-001'); });
  // Save through the existing snapshot control if the source action fixture changes.
  await frame.evaluate(() => { window.OFMEA.state.dirty = true; window.dispatchEvent(new Event('beforeunload')); });
  await expect(page.getByRole('status')).toContainText('Save failed');
  await expect(ui.locator('.toast.err').last()).toContainText('Browser save failed');
});

test('foreign messages are rejected; restored user text cannot escape its script', async ({ page }) => {
  await page.addInitScript(() => {
    const key = 'open-fmea-sharepoint-demo-v1:local-preview:preview-user:default';
    localStorage.setItem(key, JSON.stringify({manifest: {version:'1.8.3'}, projects: [],
      settings: {test: '</script><script>parent.__injected=true</script>'}}));
  });
  await open(page);
  await page.evaluate(() => window.postMessage({channel:'open-fmea-demo-v1', token:'wrong', operation:'reset'}, '*'));
  expect(await page.evaluate(() => window.__injected)).toBeUndefined();
  expect(await page.evaluate(() => localStorage.length)).toBe(1);
});
