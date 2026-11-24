'use strict';

const select = id => document.getElementById(id);
const root = document.body.dataset.root;
const cacheKey = document.body.dataset.build;
const assetUrl = path => root + path + (cacheKey ? '?v=' + cacheKey : '');
const normalize = text => text.toLocaleLowerCase('ru').replace(/ё/g, 'е');
function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = url;
    script.onload = () => { script.remove(); resolve(); };
    script.onerror = () => { script.remove(); reject(new Error('Файл данных недоступен')); };
    document.head.append(script);
  });
}

function setupCatalog() {
  const data = window.catalogData;
  const list = select('catalog');
  const rows = new Map();
  for (const row of data) {
    const item = document.createElement('li');
    item.className = 'catalog-row';
    item.dataset.id = row.id;
    const date = document.createElement('time');
    date.textContent = row.date;
    const text = document.createElement('div');
    const link = document.createElement('a');
    link.className = 'chat-title';
    link.href = row.url;
    link.textContent = row.title;
    text.append(link);
    if (row.preview) {
      const snippet = document.createElement('p');
      snippet.className = 'snippet';
      snippet.textContent = row.preview;
      text.append(snippet);
    }
    const count = document.createElement('span');
    count.className = 'row-count';
    count.textContent = row.branches + ' в. · ' + row.files + ' ф.';
    item.append(date,text,count);
    rows.set(row.id,item);
  }
  const query = select('query');
  const month = select('month');
  const sort = select('sort');
  const label = select('result-count');
  [...new Set(data.map(row => row.date.slice(0,7)))].sort().reverse().forEach(value => {
    month.add(new Option(value,value));
  });
  const cache = new Map(data.map(row => [
    row.id, normalize([row.title,row.preview,row.date,...row.tags].join('\n')),
  ]));
  let searchPromise;
  let request = 0;
  function render(matches) {
    const ids = new Set(matches.map(row => row.id));
    for (const [id,item] of rows) item.hidden = !ids.has(id);
    for (const row of matches) list.append(rows.get(row.id));
    label.textContent = matches.length ? 'Бесед: ' + matches.length : 'Беседы не найдены';
  }
  async function refresh() {
    const current = ++request;
    const term = normalize(query.value.trim());
    const terms = term.split(/\s+/).filter(Boolean);
    const range = data.filter(row => !month.value || row.date.startsWith(month.value));
    range.sort((a,b) => sort.value==='old' ? a.date.localeCompare(b.date) : b.date.localeCompare(a.date));
    if (!term) { render(range); return; }
    if (!searchPromise) {
      searchPromise = loadScript(assetUrl('data/search.js')).then(() => {
        const corpus = new Map();
        for (const row of data) corpus.set(row.id,normalize(window.archiveSearch[row.id] || ''));
        delete window.archiveSearch;
        return corpus;
      }).catch(() => null);
    }
    label.textContent = 'Поиск по репликам…';
    const corpus = await searchPromise;
    if (request !== current) return;
    render(range.filter(row => terms.every(t => cache.get(row.id).includes(t) || corpus?.get(row.id).includes(t))));
    if (!corpus) label.textContent += ' · текст реплик недоступен';
  }
  let timer;
  query.addEventListener('input',()=>{ clearTimeout(timer); timer=setTimeout(refresh,130); });
  month.addEventListener('change',refresh);
  sort.addEventListener('change',refresh);
  refresh();
}

function setupConversation(data) {
  const picker = select('branch');
  const messages = select('messages');
  const nodes = new Map([...messages.children].map(node => [node.id.slice(2),node]));
  const fork = select('fork-link');
  const summary = select('branch-summary');
  const fileList = select('file-list');
  const snapshotList = select('snapshot-list');
  const pane = select('viewer');
  const pickerVersion = select('version-select');
  const showSource = select('show-source');
  const showDiff = select('show-diff');
  const code = select('viewer-code');
  const state = select('viewer-state');
  const download = select('download-file');
  const showRaw = select('show-raw');
  let previewRequest;
  let imageUrl;
  let markdownPromise;
  let active = data.branches[0];
  let versions = [];
  let mode = 'source';
  const extension = name => name.split('.').length > 1 ? name.split('.').pop().toUpperCase() : 'ФАЙЛ';
  const formatSize = value => new Intl.NumberFormat('ru',{maximumFractionDigits:1}).format(value/1024) + ' КБ';
  const branchName = id => id ? 'Ветвь ' + id : 'Главная ветвь';

  const escapeHtml = text => text.replace(/[&<>"']/g, ch => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  })[ch]);

  async function renderMarkdown(text) {
    markdownPromise ??= loadScript(assetUrl('assets/marked.js')).catch(() => null);
    await markdownPromise;
    const library = window.marked;
    if (!library) return null;
    const renderer = new library.Renderer();
    renderer.html = ({text}) => escapeHtml(text);
    renderer.image = ({text}) => '<span>[Изображение: ' + escapeHtml(text || 'без подписи') + ']</span>';
    renderer.link = function ({href,tokens}) {
      const caption = this.parser.parseInline(tokens);
      return /^https?:\/\//i.test(href)
        ? '<a target="_blank" rel="noopener noreferrer" href="' + escapeHtml(href) + '">' + caption + '</a>'
        : caption;
    };
    return library.marked.parse(text,{renderer,gfm:true});
  }

  function setMode(value) {
    mode = value;
    renderVersion();
  }

  function clearPreview() {
    code.replaceChildren();
    if (imageUrl) URL.revokeObjectURL(imageUrl);
    imageUrl = undefined;
  }

  function insertText(text, diff) {
    const pre = document.createElement('pre');
    if (!diff) pre.textContent = text;
    else {
      const classes = {'+':'diff-add','-':'diff-remove','@':'diff-hunk'};
      const lines = document.createDocumentFragment();
      for (const line of text.split('\n')) {
        const span = document.createElement('span');
        span.className = classes[line[0]] || '';
        span.textContent = line + '\n';
        lines.append(span);
      }
      pre.append(lines);
    }
    code.append(pre);
  }

  async function readText(response) {
    const cap = 500_000;
    if (!response.body || typeof response.body.getReader !== 'function') {
      const data = new Uint8Array(await response.arrayBuffer());
      return {bytes:data.subarray(0,cap),limited:data.length > cap};
    }
    const reader = response.body.getReader();
    const bytes = new Uint8Array(cap);
    let count = 0;
    while (true) {
      const {done,value} = await reader.read();
      if (done) break;
      const used = Math.min(value.length, cap-count);
      bytes.set(value.subarray(0,used),count);
      count += used;
      if (used < value.length) {
        await reader.cancel();
        return {bytes,limited:true};
      }
    }
    return {bytes:bytes.subarray(0,count),limited:false};
  }

  async function renderVersion() {
    const version = versions[Number(pickerVersion.value)];
    if (!version) return;
    if (previewRequest) previewRequest.abort();
    const request = new AbortController();
    previewRequest = request;
    clearPreview();
    const format = extension(version.name);
    const markdown = /^(MD|MARKDOWN)$/.test(format);
    if ((mode === 'diff' && !version.previous) || (mode === 'raw' && !markdown)) mode = 'source';
    showSource.setAttribute('aria-pressed',String(mode === 'source'));
    showRaw.setAttribute('aria-pressed',String(mode === 'raw'));
    showRaw.hidden = !markdown;
    showDiff.setAttribute('aria-pressed',String(mode === 'diff'));
    showDiff.disabled = !version.previous;
    select('viewer-title').textContent = version.name;
    select('viewer-info').textContent = version.source + ' · ' + formatSize(version.size);
    download.href = root + version.file;
    download.download = version.name;
    const preview = mode === 'diff' ? version.diff : version.file;
    code.hidden = true;
    if (!preview) {
      state.textContent = 'Предпросмотр изменений для этой версии недоступен. Обе версии можно скачать.';
      return;
    }
    if (location.protocol === 'file:') {
      state.textContent = 'Для предпросмотра откройте архив через start.cmd или python start.py.';
      return;
    }
    state.textContent = 'Загрузка…';
    try {
      const response = await fetch(root + preview,{signal:request.signal,cache:'no-cache'});
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const images = {PNG:'image/png',JPG:'image/jpeg',JPEG:'image/jpeg',GIF:'image/gif',WEBP:'image/webp',AVIF:'image/avif'};
      if (mode === 'source' && Object.prototype.hasOwnProperty.call(images,format)) {
        const bytes = await response.arrayBuffer();
        if (request.signal.aborted) return;
        imageUrl = URL.createObjectURL(new Blob([bytes],{type:images[format]}));
        const image = document.createElement('img');
        image.src = imageUrl;
        image.alt = version.name;
        code.append(image);
        code.hidden = false;
        state.textContent = '';
        return;
      }
      const {bytes,limited} = await readText(response);
      if (request.signal.aborted) return;
      let text;
      try {
        text = new TextDecoder('utf-8',{fatal:true}).decode(bytes,{stream:limited});
      } catch {
        text = null;
      }
      if (text === null || text.includes('\u0000')) {
        state.textContent = 'Предпросмотр этого формата недоступен. Файл можно скачать.';
        return;
      }
      state.textContent = limited ? 'Показано начало файла. Можно скачать полную версию.' : '';
      if (markdown && mode === 'source' && !limited) {
        const rendered = await renderMarkdown(text);
        if (request.signal.aborted) return;
        if (rendered === null) insertText(text,false);
        else {
          const article = document.createElement('div');
          article.className = 'prose markdown-preview';
          article.innerHTML = rendered;
          code.append(article);
        }
      } else insertText(text,mode === 'diff');
      code.hidden = false;
    } catch (error) {
      if (!request.signal.aborted) state.textContent = 'Не удалось загрузить предпросмотр · ' + error.message;
    }
  }

  function openFile(list) {
    versions=list;
    pickerVersion.replaceChildren();
    list.forEach((v,i) => {
      const title=v.message ? branchName(v.branch)+' · #'+v.label+' · '+v.when : 'Снимок из выгрузки · '+branchName(v.branch);
      pickerVersion.add(new Option(title,String(i)));
    });
    pickerVersion.disabled=list.length===1;
    pickerVersion.selectedIndex=0;
    if (!pane.open) pane.showModal();
    setMode('source');
  }

  function fileButton(list, snapshot) {
    const v=list[0];
    const button=document.createElement('button');
    button.type='button';
    button.className='file-row';
    const ext=document.createElement('span');
    ext.className='ext';
    ext.textContent=extension(v.name);
    const content=document.createElement('span');
    const name=document.createElement('strong');
    name.textContent=v.name;
    const detail=document.createElement('small');
    detail.textContent=snapshot?v.source:
      (list.length===1?'1 версия':list.length+' вер.')+(v.branch!==active.id?' · из '+(v.branch?'ветви '+v.branch:'главной ветви'):'');
    content.append(name,detail);
    button.append(ext,content);
    button.addEventListener('click',()=>openFile(list));
    return button;
  }

  const forkControls = [];

  function mountForkControls() {
    const groups = new Map();
    for (const branch of data.branches.slice(1)) {
      if (!groups.has(branch.origin)) groups.set(branch.origin, []);
      groups.get(branch.origin).push(branch);
    }
    for (const [origin, alternatives] of groups) {
      const owner = data.branches.find(branch => branch.id === (alternatives[0].parent ?? 0));
      const continuation = branch => origin
        ? branch.chain[branch.chain.indexOf(origin) + 1]
        : branch.chain[0];
      const options = [owner, ...alternatives].filter(branch => branch && continuation(branch));
      if (options.length < 2) continue;
      const anchor = origin ? nodes.get(origin) : messages;
      if (!anchor) continue;

      const controls = document.createElement('div');
      controls.className = 'fork-controls';
      const title = document.createElement('span');
      title.textContent = origin ? 'Продолжение' : 'Начало беседы';
      const previous = document.createElement('button');
      const next = document.createElement('button');
      for (const [button, symbol, label] of [
        [previous, '←', 'Предыдущий вариант'],
        [next, '→', 'Следующий вариант'],
      ]) {
        button.type = 'button';
        button.textContent = symbol;
        button.setAttribute('aria-label', label);
      }
      const choice = document.createElement('select');
      choice.setAttribute('aria-label', origin ? 'Вариант продолжения' : 'Вариант начала беседы');
      options.forEach((branch, index) => choice.add(new Option(
        (index + 1) + ' / ' + options.length + ' · ' +
        branchName(branch.id),
        String(index)
      )));
      controls.append(title, previous, choice, next);
      if (origin) anchor.querySelector('.prose').before(controls);
      else messages.before(controls);

      function choose(index, button) {
        const branch = options[index];
        if (!branch) return;
        const y = anchor.getBoundingClientRect().top;
        showBranch(branch.id);
        history.replaceState(null, '', '#b-' + branch.id);
        window.scrollBy(0, anchor.getBoundingClientRect().top - y);
        if (button?.disabled) choice.focus({preventScroll: true});
      }
      previous.addEventListener('click', () => choose(Number(choice.value) - 1, previous));
      next.addEventListener('click', () => choose(Number(choice.value) + 1, next));
      choice.addEventListener('change', () => choose(Number(choice.value)));
      forkControls.push(branch => {
        if (origin && !branch.chain.includes(origin)) return;
        const index = options.findIndex(option => continuation(option) === continuation(branch));
        if (index < 0) {
          controls.hidden = true;
          return;
        }
        controls.hidden = false;
        choice.value = String(index);
        previous.disabled = index === 0;
        next.disabled = index === options.length - 1;
      });
    }
  }

  function showBranch(value) {
    active=data.branches.find(branch => branch.id===Number(value)) || data.branches[0];
    picker.value=String(active.id);
    const chain = new Set(active.chain);
    for (const [id,node] of nodes) node.hidden=!chain.has(id);
    for (const id of chain) messages.append(nodes.get(id));
    for (const sync of forkControls) sync(active);
    fork.hidden=!active.origin;
    if (active.origin) fork.href='#m-'+active.origin;
    summary.textContent=active.id
      ? (active.origin?'После реплики '+active.originLabel+' · ':'От начала беседы · ')+active.tail.length+' реплик в продолжении'
      : active.tail.length+' реплик в главной ветви';
    const groups=new Map();
    for (const event of active.events) {
      const v=data.events[event];
      if (!groups.has(v.f)) groups.set(v.f,[]);
      groups.get(v.f).unshift(v);
    }
    const items=[...groups.values()].sort((a,b)=>a[0].name.localeCompare(b[0].name,'ru'));
    select('file-state').textContent=items.length
      ? 'Файлов в выбранной ветке: '+items.length+(active.missed?' · пропущено правок: '+active.missed:'')
      : 'Нет восстановленных версий для этой ветки.';
    fileList.replaceChildren(...items.map(list=>fileButton(list,false)));
    const snapshots=data.archive.filter(v=>v.branch===active.id);
    select('archived-files').hidden=!snapshots.length;
    select('snapshot-count').textContent='· '+snapshots.length;
    snapshotList.replaceChildren(...snapshots.map(v=>fileButton([v],true)));
  }

  function jumpToHash() {
    const branchLink = /^#b-(\d+)$/.exec(location.hash);
    if (branchLink) {
      showBranch(branchLink[1]);
      return;
    }
    const hash = location.hash;
    const tool = hash.startsWith('#tool-') ? select(hash.slice(1)) : null;
    const id = tool ? tool.closest('.message').id.slice(2) : hash.startsWith('#m-') ? hash.slice(3) : '';
    if (!nodes.has(id)) return;
    if (!active.chain.includes(id)) {
      const branch=data.branches.find(b=>b.tail.includes(id));
      if (branch) showBranch(branch.id);
    }
    if (tool) {
      for (let node = tool; node && node.id !== 'm-' + id; node = node.parentElement) {
        if (node.tagName === 'DETAILS') node.open = true;
      }
    }
    requestAnimationFrame(() => (tool || nodes.get(id)).scrollIntoView({block:'start'}));
  }

  picker.addEventListener('change', () => {
    showBranch(picker.value);
    history.replaceState(null, '', '#b-' + active.id);
  });
  window.addEventListener('hashchange',jumpToHash);
  messages.addEventListener('click', event => {
    const action = event.target.closest('button[data-tools]');
    if (!action) return;
    const series = action.closest('.tool-series');
    const open = action.dataset.tools === 'open';
    for (const item of series.querySelectorAll('details')) item.open = open;
    if (!open) {
      series.open = false;
      series.querySelector('summary').focus();
    }
  });
  pickerVersion.addEventListener('change',renderVersion);
  select('viewer-close').addEventListener('click',()=>pane.close());
  select('back-to-messages').addEventListener('click',()=>picker.scrollIntoView({block:'center'}));
  showDiff.addEventListener('click',()=>setMode('diff'));
  showSource.addEventListener('click',()=>setMode('source'));
  showRaw.addEventListener('click',()=>setMode('raw'));
  pane.addEventListener('close',() => {
    if (previewRequest) previewRequest.abort();
    clearPreview();
  });
  mountForkControls();
  showBranch(0);
  jumpToHash();
}

if (window.catalogData) setupCatalog();
const conversationData = select('conversation-data');
if (conversationData) setupConversation(JSON.parse(conversationData.textContent));
