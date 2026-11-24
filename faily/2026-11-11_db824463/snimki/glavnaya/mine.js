/* Wittgenstein's Nachlass (BEE) — "My work": bookmarks, highlights, notes (kept in this browser),
   with export to and import from a JSON file. */
(function () {
  'use strict';
  var t = BEE.t, LS = BEE.LS, $ = function (id) { return document.getElementById(id); };
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function date(ts) { try { return new Date(ts).toLocaleString(BEE.lang()); } catch (e) { return ''; } }
  function render() {
    var bm = LS.get('bookmarks', []), mk = LS.get('marks', []), notes = LS.get('notes', []);
    $('bm').innerHTML = bm.length ? '<table>' + bm.map(function (b, i) {
      return '<tr><td><a href="' + esc(b.href) + '">' + esc(b.title) + '</a> ' + esc(b.page || '') + '</td><td class="muted">' + date(b.ts) + '</td><td><button data-del-bm="' + i + '">✕</button></td></tr>';
    }).join('') + '</table>' : '<p class="muted">' + t('mine.empty') + '</p>';
    var col = $('mk-color').value;
    var ms = mk.filter(function (m) { return !col || String(m.color) === col; });
    $('mk').innerHTML = ms.length ? '<table>' + ms.map(function (m) {
      return '<tr><td><span class="hl' + m.color + '">' + esc(m.text) + '</span><div class="muted">' + esc(m.src || m.title) + (m.comment ? ' — ' + esc(m.comment) : '') + '</div></td><td><a href="' + esc(m.page) + '">→</a></td><td class="muted">' + date(m.ts) + '</td><td><button data-del-mk="' + esc(m.id) + '">✕</button></td></tr>';
    }).join('') + '</table>' : '<p class="muted">' + t('mine.empty') + '</p>';
    var cur = LS.get('curnote', notes[0] && notes[0].id);
    $('nt-list').innerHTML = notes.map(function (n) { return '<option value="' + n.id + '"' + (n.id === cur ? ' selected' : '') + '>' + esc((n.text || '…').slice(0, 40)) + '</option>'; }).join('');
    var nn = notes.filter(function (n) { return n.id === cur; })[0] || notes[0];
    $('nt').value = nn ? nn.text : ''; $('nt').disabled = !nn;
    document.querySelectorAll('[data-del-bm]').forEach(function (b) { b.onclick = function () { bm.splice(+b.dataset.delBm, 1); LS.set('bookmarks', bm); render(); }; });
    document.querySelectorAll('[data-del-mk]').forEach(function (b) { b.onclick = function () { LS.set('marks', mk.filter(function (m) { return m.id !== b.dataset.delMk; })); render(); }; });
  }
  function init() {
    $('mk-color').onchange = render;
    $('nt-new').onclick = function () { var n = LS.get('notes', []), x = { id: 'n' + Date.now(), text: '', ts: Date.now() }; n.push(x); LS.set('notes', n); LS.set('curnote', x.id); render(); };
    $('nt-del').onclick = function () { var cur = $('nt-list').value; LS.set('notes', LS.get('notes', []).filter(function (n) { return n.id !== cur; })); render(); };
    $('nt-list').onchange = function () { LS.set('curnote', this.value); render(); };
    $('nt').oninput = function () { var n = LS.get('notes', []), cur = $('nt-list').value; n.forEach(function (x) { if (x.id === cur) { x.text = $('nt').value; x.ts = Date.now(); } }); LS.set('notes', n); };
    $('exp').onclick = function () {
      var data = { app: 'bee-site', version: 1, bookmarks: LS.get('bookmarks', []), marks: LS.get('marks', []), notes: LS.get('notes', []) };
      var a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 1)], { type: 'application/json' }));
      a.download = 'bee-meine-arbeit.json'; a.click();
    };
    $('imp').onchange = function () {
      var f = this.files[0]; if (!f) return; var r = new FileReader();
      r.onload = function () {
        try {
          var d = JSON.parse(r.result);
          ['bookmarks', 'marks', 'notes'].forEach(function (k) {
            var have = LS.get(k, []), seen = {}; have.forEach(function (x) { seen[x.id || x.href + x.ts] = 1; });
            (d[k] || []).forEach(function (x) { if (!seen[x.id || x.href + x.ts]) have.push(x); }); LS.set(k, have);
          });
          render();
        } catch (e) { alert(t('mine.badfile')); }
      };
      r.readAsText(f);
    };
    render();
    document.addEventListener('bee-lang', render);
  }
  init();
})();
