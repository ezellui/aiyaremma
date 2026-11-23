'use strict';

const select = id => document.getElementById(id);
const root = document.body.dataset.root;
const normalize = text => text.toLocaleLowerCase('ru').replace(/ё/g, 'е');
const loadedBlobs = new Map();
const blobRequests = new Map();

window.storeArchiveBlob = (key, encoded) => loadedBlobs.set(key, encoded);

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = url;
    script.onload = () => { script.remove(); resolve(); };
    script.onerror = () => { script.remove(); reject(new Error('Файл данных недоступен')); };
    document.head.append(script);
  });
}

function loadBlob(key) {
  if (!blobRequests.has(key)) {
    blobRequests.set(key, loadScript(root + 'data/blobs/' + key + '.js').then(() => {
      const encoded = loadedBlobs.get(key);
      if (encoded === undefined) throw new Error('Файл данных повреждён');
      return Uint8Array.from(atob(encoded), char => char.charCodeAt(0));
    }).catch(error => { blobRequests.delete(key); throw error; }));
  }
  return blobRequests.get(key);
}

function setupCatalog() {
  const data = window.catalogData;
  const list = select('catalog');
  const rows = new Map([...list.children].map(item => [item.dataset.id,item]));
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
      searchPromise = loadScript('data/search.js').then(() => {
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

function setupConversation() {
  const data = window.conversationData;
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
  let active = data.branches[0];
  let versions = [];
  let mode = 'source';
  let viewRequest = 0;
  const extension = name => name.split('.').length > 1 ? name.split('.').pop().toUpperCase() : 'ФАЙЛ';
  const formatSize = value => new Intl.NumberFormat('ru',{maximumFractionDigits:1}).format(value/1024) + ' КБ';
  const branchName = id => id ? 'Ветвь ' + id : 'Главная ветвь';

  function setMode(value) {
    mode=value;
    showSource.setAttribute('aria-pressed',String(value==='source'));
    showDiff.setAttribute('aria-pressed',String(value==='diff'));
    renderVersion();
  }

  async function renderVersion() {
    const v = versions[Number(pickerVersion.value)];
    const current = ++viewRequest;
    if (!v) return;
    select('viewer-title').textContent=v.name;
    select('viewer-info').textContent=v.source + ' · ' + formatSize(v.size);
    showDiff.disabled = !v.previous;
    if (mode==='diff' && !v.previous) {
      mode='source';
      showSource.setAttribute('aria-pressed','true');
      showDiff.setAttribute('aria-pressed','false');
    }
    code.classList.toggle('diff',mode==='diff');
    code.replaceChildren();
    if (mode==='diff' && !v.diff) {
      state.textContent='Предпросмотр изменений для этой версии недоступен. Обе версии можно скачать.';
      return;
    }
    state.textContent='Загрузка…';
    try {
      const bytes=await loadBlob(mode==='diff'?v.diff:v.blob);
      if (current!==viewRequest) return;
      const limited=bytes.length>500_000;
      const text=new TextDecoder().decode(limited?bytes.subarray(0,500_000):bytes);
      state.textContent=limited?'Показано начало файла. Кнопка «Скачать» сохраняет полную версию.':'';
      if (mode==='diff') {
        const lines=document.createDocumentFragment();
        for (const line of text.split('\n')) {
          const node=document.createElement('span');
          node.className=line.startsWith('+')?'diff-add':line.startsWith('-')?'diff-remove':line.startsWith('@@')?'diff-hunk':'';
          node.textContent=line+'\n';
          lines.append(node);
        }
        code.append(lines);
      } else code.textContent=text;
    } catch (error) {
      if (current===viewRequest) state.textContent=error.message;
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

  function showBranch(value) {
    active=data.branches.find(branch => branch.id===Number(value)) || data.branches[0];
    picker.value=String(active.id);
    const chain = new Set(active.chain);
    for (const [id,node] of nodes) node.hidden=!chain.has(id);
    for (const id of chain) messages.append(nodes.get(id));
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
    if (!location.hash.startsWith('#m-')) return;
    const id=location.hash.slice(3);
    if (!nodes.has(id)) return;
    if (!active.chain.includes(id)) {
      const branch=data.branches.find(b=>b.tail.includes(id));
      if (branch) showBranch(branch.id);
    }
    requestAnimationFrame(()=>nodes.get(id).scrollIntoView({block:'start'}));
  }

  picker.addEventListener('change',()=>showBranch(picker.value));
  window.addEventListener('hashchange',jumpToHash);
  pickerVersion.addEventListener('change',renderVersion);
  select('viewer-close').addEventListener('click',()=>pane.close());
  select('back-to-messages').addEventListener('click',()=>picker.scrollIntoView({block:'center'}));
  showDiff.addEventListener('click',()=>setMode('diff'));
  showSource.addEventListener('click',()=>setMode('source'));
  select('download-file').addEventListener('click',async () => {
    const v=versions[Number(pickerVersion.value)];
    try {
      const bytes=await loadBlob(v.blob);
      const url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'}));
      const link=document.createElement('a');
      link.href=url;
      link.download=v.name;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
    } catch (error) {
      state.textContent=error.message;
    }
  });
  showBranch(0);
  jumpToHash();
}

if (window.catalogData) setupCatalog();
if (window.conversationData) setupConversation();
