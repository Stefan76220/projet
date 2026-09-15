const root = document.getElementById('document');
const statusNode = document.getElementById('status');
const state = {
  editors: [],
  loading: false,
  generation: 0,
  boot: 'host_js_loaded',
  vendor: 'not_loaded',
  lastError: null,
};

function post(type, details = {}) {
  try {
    if (window.ipc && typeof window.ipc.postMessage === 'function') {
      window.ipc.postMessage(JSON.stringify({ type, ...details }));
      return true;
    }
  } catch (_) {}
  return false;
}

function errorText(error) {
  if (!error) return 'Erreur JavaScript inconnue';
  const message = String(error?.message || error);
  const stack = error?.stack ? String(error.stack) : '';
  return stack && !stack.includes(message) ? `${message}\n${stack}` : (stack || message);
}

function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
function nextFrame() { return new Promise(resolve => requestAnimationFrame(() => resolve())); }

async function loadEditorClass() {
  if (window.__TL_CANVAS_EDITOR_CLASS__) return window.__TL_CANVAS_EDITOR_CLASS__;
  state.vendor = 'loading';
  try {
    const module = await import('./vendor/canvas-editor.js');
    const Editor = module?.default || module?.Editor;
    if (typeof Editor !== 'function') {
      throw new Error('Canvas Editor chargé mais export Editor introuvable');
    }
    window.__TL_CANVAS_EDITOR_CLASS__ = Editor;
    state.vendor = 'ready';
    post('vendor_loaded', { canvasEditorVersion: '1.0.2' });
    return Editor;
  } catch (error) {
    state.vendor = 'failed';
    state.lastError = errorText(error);
    post('error', { stage: 'vendor_import', message: state.lastError });
    throw error;
  }
}

function destroyEditors() {
  for (const editor of state.editors) {
    try { editor.destroy(); } catch (_) {}
  }
  state.editors = [];
  root.replaceChildren();
  root.classList.remove('ready');
  root.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('ready');
}

function segmentPageCount(segmentNode) {
  const indexed = segmentNode.querySelectorAll('canvas[data-index]').length;
  if (indexed > 0) return indexed;
  return segmentNode.querySelectorAll('canvas').length;
}

async function waitForStablePagination(segmentNodes, generation) {
  let previous = -1;
  let stableFrames = 0;
  for (let pass = 0; pass < 160; pass += 1) {
    if (generation !== state.generation) throw new Error('Chargement remplacé');
    await nextFrame();
    await sleep(25);
    const count = segmentNodes.reduce((sum, node) => sum + segmentPageCount(node), 0);
    const measurable = segmentNodes.every(node => node.getBoundingClientRect().width > 0);
    if (count > 0 && measurable && count === previous) stableFrames += 1;
    else stableFrames = 0;
    previous = count;
    if (stableFrames >= 4) return count;
  }
  throw new Error('Pagination Canvas Editor non stabilisée');
}

function normalizedOptions(options = {}) {
  return {
    ...options,
    pageMode: 'paging',
    defaultType: 'TEXT',
    defaultFont: 'Arial',
    defaultSize: 16,
    minSize: 1,
    maxSize: 200,
    pageGap: 12,
    scale: 1,
  };
}

window.tomeLineaCanvasLoad = async function tomeLineaCanvasLoad(plan) {
  if (state.loading) state.generation += 1;
  const generation = ++state.generation;
  state.loading = true;
  state.boot = 'loading_document';
  state.lastError = null;
  destroyEditors();
  statusNode.textContent = 'Préparation du document…';

  try {
    const Editor = await loadEditorClass();
    if (generation !== state.generation) return;

    const segments = Array.isArray(plan?.render_segments) ? plan.render_segments : [];
    if (!segments.length) throw new Error('Aucun segment de rendu');

    const nodes = [];
    for (const segment of segments) {
      const node = document.createElement('section');
      node.className = 'segment';
      node.dataset.segment = String(segment.segment ?? nodes.length + 1);
      root.appendChild(node);
      const editor = new Editor(
        node,
        segment.data || { main: [] },
        normalizedOptions(segment.options || {})
      );
      state.editors.push(editor);
      nodes.push(node);
    }
    state.boot = 'canvas_created';
    post('canvas_created', { segmentCount: nodes.length });

    if (document.fonts?.ready) await document.fonts.ready;
    if (generation !== state.generation) return;
    state.boot = 'fonts_loaded';
    post('fonts_loaded');

    await nextFrame();
    await nextFrame();
    if (generation !== state.generation) return;
    state.boot = 'layout_complete';
    post('layout_complete');

    const pageCount = await waitForStablePagination(nodes, generation);
    if (generation !== state.generation) return;
    state.boot = 'pagination_stable';
    post('pagination_stable', { pageCount });

    await nextFrame();
    root.classList.add('ready');
    root.setAttribute('aria-hidden', 'false');
    document.body.classList.add('ready');
    state.loading = false;
    state.boot = 'render_complete';
    post('render_complete', { pageCount });
  } catch (error) {
    state.loading = false;
    state.boot = 'failed';
    state.lastError = errorText(error);
    statusNode.textContent = 'Le document n’a pas pu être préparé.';
    // vendor_import a déjà envoyé une erreur précise. Pour les autres erreurs,
    // envoyer l'étape render afin que Python arrête immédiatement le test.
    if (state.vendor !== 'failed') {
      post('error', { stage: 'render', message: state.lastError });
    }
  }
};

window.tomeLineaCanvasStatus = function tomeLineaCanvasStatus() {
  return {
    host: 'loaded',
    boot: state.boot,
    vendor: state.vendor,
    ipc: !!(window.ipc && typeof window.ipc.postMessage === 'function'),
    editors: state.editors.length,
    loading: state.loading,
    ready: root.classList.contains('ready'),
    pages: [...root.querySelectorAll('.segment')].reduce((sum, node) => sum + segmentPageCount(node), 0),
    lastError: state.lastError,
    href: location.href,
  };
};


window.tomeLineaCanvasBoot = {
  host: 'loaded',
  version: '2.8',
  ipc: !!(window.ipc && typeof window.ipc.postMessage === 'function'),
};
post('host_loaded', { canvasEditorVersion: '1.0.2', hostVersion: '2.8' });
