import { DemoHost, createStorageKey } from '../src/demo/DemoHost';
const params = new URLSearchParams(location.search);
const root = document.getElementById('demo');
if (!root) throw new Error('Missing preview root');
const host = new DemoHost(root, createStorageKey('local-preview', 'preview-user', params.get('instance') || 'default'));
host.mount(900);
