import { demoHtml } from './demoHtml';

const channel = 'open-fmea-demo-v1';
const maxSnapshotLength = 4 * 1024 * 1024;

export function createStorageKey(siteId: string, userId: string, instanceId: string): string {
  return ['open-fmea-sharepoint-demo-v1', siteId, userId, instanceId]
    .map(encodeURIComponent).join(':');
}

export function createFrameHtml(token: string, origin: string, snapshot: ReturnType<Storage['getItem']>): string {
  // A stored container may contain arbitrary user text, including a closing script tag.
  const config = JSON.stringify({ token, origin, snapshot })
    .replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
  return demoHtml.replace('<!--__OPEN_FMEA_HOST_CONFIG__-->',
    '<script>window.__openFmeaHostConfig=' + config + ';</script>');
}

export class DemoHost {
  private frame: HTMLIFrameElement | undefined;
  private status: HTMLSpanElement | undefined;
  private token = '';
  private disposed = false;

  public constructor(private readonly root: HTMLElement, private readonly storageKey: string) {
    window.addEventListener('message', this.onMessage);
  }

  public mount(height: number): void {
    if (this.disposed) return;
    // Property-pane rerenders must not discard the active in-memory session.
    if (this.frame) {
      this.frame.style.height = `${Math.max(600, Math.min(1600, height || 900))}px`;
      return;
    }
    this.token = Array.from(crypto.getRandomValues(new Uint32Array(4)))
      .map(value => value.toString(16)).join('-');
    let snapshot: string | null = null;
    let storageError = '';
    try { snapshot = window.localStorage.getItem(this.storageKey); }
    catch (error) { storageError = String(error); }

    const bar = document.createElement('div');
    bar.style.cssText = 'padding:10px 14px;background:#06213b;color:white;display:flex;gap:16px;flex-wrap:wrap;font:13px Segoe UI,sans-serif';
    const label = document.createElement('strong');
    label.textContent = 'Open FMEA · SharePoint Demo';
    const notice = document.createElement('span');
    notice.textContent = 'Personal browser storage · data is not shared with your team';
    this.status = document.createElement('span');
    this.status.setAttribute('role', 'status');
    this.status.setAttribute('aria-live', 'polite');
    this.status.style.marginLeft = 'auto';
    this.status.textContent = storageError ? 'Browser storage unavailable. Use container export.' :
      snapshot ? 'Browser snapshot loaded' : 'Embedded demo data';
    bar.append(label, notice, this.status);

    const frame = document.createElement('iframe');
    frame.title = 'Open FMEA engineering demo';
    // The opaque frame cannot access SharePoint cookies, DOM, or APIs.
    frame.setAttribute('sandbox', 'allow-scripts allow-downloads allow-modals');
    frame.style.cssText = 'display:block;width:100%;border:0;background:#f5f7fb;';
    frame.style.height = `${Math.max(600, Math.min(1600, height || 900))}px`;
    frame.srcdoc = createFrameHtml(this.token, window.location.origin, snapshot);
    this.frame = frame;
    this.root.replaceChildren(bar, frame);
  }

  private readonly onMessage = (event: MessageEvent): void => {
    if (!this.frame || event.source !== this.frame.contentWindow || event.origin !== 'null') return;
    const message = event.data;
    if (!message || message.channel !== channel || message.token !== this.token) return;
    if (message.operation !== 'save' && message.operation !== 'reset') return;
    let ok = false;
    let errorText = '';
    try {
      if (message.operation === 'reset') {
        window.localStorage.removeItem(this.storageKey);
        const height = Number.parseInt(this.frame.style.height, 10);
        this.frame.remove();
        this.frame = undefined;
        this.mount(height);
        return;
      }
      if (typeof message.snapshot !== 'string' || message.snapshot.length > maxSnapshotLength) {
        throw new Error('Snapshot exceeds the demo storage limit.');
      }
      const value = JSON.parse(message.snapshot);
      if (!value || !value.manifest || !Array.isArray(value.projects)) {
        throw new Error('Invalid Open FMEA snapshot.');
      }
      window.localStorage.setItem(this.storageKey, message.snapshot);
      ok = true;
      if (this.status) this.status.textContent = 'Saved in this browser · ' + new Date().toLocaleTimeString();
    } catch (error) {
      errorText = String(error);
      if (this.status) this.status.textContent = 'Save failed. Export your container to keep changes.';
    }
    // '*' is required to address this opaque-origin sandbox; source+token are checked on both sides.
    this.frame?.contentWindow?.postMessage({ channel, token: this.token,
      operation: 'save-result', sequence: message.sequence, ok, error: errorText }, '*');
  };

  public dispose(): void {
    this.disposed = true;
    window.removeEventListener('message', this.onMessage);
    this.frame = undefined;
    this.root.replaceChildren();
  }
}
