(() => {
  console.group('%c[Runt Diagnostic v2]',
    'background:#3a2614;color:#fef8e7;padding:4px 10px;border-radius:3px;font-weight:bold');

  // ── Локальный analyzeRunt (копия из спеки) ──
  const RUNT_MAX_LINE_WIDTH_PX = 60;
  const RUNT_MAX_LINE_FRACTION = 0.25;

  function localAnalyzeRunt(p) {
    if (!p.isConnected) return null;
    if (p.classList && p.classList.contains('no-runt-hang')) return null;
    const range = document.createRange();
    range.selectNodeContents(p);
    const rawRects = range.getClientRects();
    const byLine = [];
    for (const r of rawRects) {
      if (r.width === 0 || r.height === 0) continue;
      const line = byLine.find(l => Math.abs(l.top - r.top) < 3);
      if (line) {
        line.left = Math.min(line.left, r.left);
        line.right = Math.max(line.right, r.right);
        line.width = line.right - line.left;
      } else {
        byLine.push({ top: r.top, left: r.left, right: r.right, width: r.width });
      }
    }
    if (byLine.length < 2) return null;
    byLine.sort((a, b) => a.top - b.top);
    const last = byLine[byLine.length - 1];
    const penult = byLine[byLine.length - 2];
    const isRunt = last.width < RUNT_MAX_LINE_WIDTH_PX ||
                   (last.width / penult.width) < RUNT_MAX_LINE_FRACTION;
    if (!isRunt) return null;
    return {
      lineCount: byLine.length,
      lastLineWidth: last.width,
      penultLineWidth: penult.width,
      widthFraction: last.width / penult.width
    };
  }

  function paragraphLabel(p) {
    const folios = Array.from(document.querySelectorAll('.folio'));
    const folio = p.closest('.folio');
    const folioIdx = folio ? folios.indexOf(folio) + 1 : '?';
    const text = (p.textContent || '').replace(/\s+/g, ' ').trim();
    const preview = text.length > 60 ? text.slice(0, 60) + '…' : text;
    const tail = p.querySelector('.runt-hang') || p;
    const fam = ((getComputedStyle(tail).fontFamily) || '').toLowerCase();
    let font = '?';
    if (fam.indexOf('uncialis') !== -1) font = 'Uncialis';
    else if (fam.indexOf('remedius') !== -1) font = 'Remedius';
    else if (fam.indexOf('beda') !== -1) font = 'Beda';
    else if (fam.indexOf('kells') !== -1) font = 'Kells';
    return { folio: folioIdx, preview, font };
  }

  // ── Часть 1. Анализ через DOM (как и раньше) ──
  const allPs = Array.from(document.querySelectorAll('#codex-book p'));
  const result = {
    total: allPs.length,
    skipped: 0,
    skipReasons: { marginalia: 0, rubric: 0, theological: 0, dropcap: 0, noRuntHang: 0 },
    eligible: 0,
    cleanParagraphs: 0,
    fixedB: [],
    fixedC: [],
    runtsRemaining: []
  };

  for (const p of allPs) {
    if (p.classList.contains('marginalia')) { result.skipped++; result.skipReasons.marginalia++; continue; }
    if (p.classList.contains('rubric')) { result.skipped++; result.skipReasons.rubric++; continue; }
    if (p.classList.contains('theological')) { result.skipped++; result.skipReasons.theological++; continue; }
    if (p.classList.contains('dropcap')) { result.skipped++; result.skipReasons.dropcap++; continue; }
    if (p.classList.contains('no-runt-hang')) { result.skipped++; result.skipReasons.noRuntHang++; continue; }
    result.eligible++;

    const runtHangSpan = p.querySelector('.runt-hang');
    const compressedWs = p.querySelectorAll('.ws[data-w0]');
    const label = paragraphLabel(p);

    if (runtHangSpan) {
      result.fixedC.push({
        ...label,
        hangX: runtHangSpan.style.getPropertyValue('--runt-hang-x') || '?',
        word: (runtHangSpan.textContent || '').trim().slice(0, 30),
        el: p
      });
    } else if (compressedWs.length > 0) {
      result.fixedB.push({
        ...label,
        wsCompressed: compressedWs.length,
        el: p
      });
    } else {
      const runt = localAnalyzeRunt(p);
      if (runt) {
        result.runtsRemaining.push({
          ...label,
          lastWidth_px: Math.round(runt.lastLineWidth),
          fraction_pct: Math.round(runt.widthFraction * 100),
          lines: runt.lineCount,
          el: p
        });
      } else {
        result.cleanParagraphs++;
      }
    }
  }

  const lastwordCount = document.querySelectorAll('.lastword-no-wbr').length;

  // ── Часть 2. Анализ детального лога из window.__runtPreventionLog ──
  const detailLog = window.__runtPreventionLog;
  const hasDetailLog = Array.isArray(detailLog) && detailLog.length > 0;

  // ── Сводка ──
  console.log('%cСводка:', 'font-weight:bold;font-size:1.05em');
  console.log(`  Всего <p>: %c${result.total}`, 'font-weight:bold');
  console.log(`  Пропущено: ${result.skipped} ` +
              `[marginalia ${result.skipReasons.marginalia}, ` +
              `rubric ${result.skipReasons.rubric}, ` +
              `theological ${result.skipReasons.theological}, ` +
              `dropcap ${result.skipReasons.dropcap}, ` +
              `no-runt-hang ${result.skipReasons.noRuntHang}]`);
  console.log(`  Eligible: %c${result.eligible}`, 'font-weight:bold');
  console.log('');
  console.log(`  ├─ Стратегия A (lastword-no-wbr): %c${lastwordCount}%c слов помечено`,
              'font-weight:bold;color:#2a7', '');
  console.log(`  ├─ Стратегия B (compression):    %c${result.fixedB.length}%c успех`,
              'font-weight:bold;color:#27a', '');
  console.log(`  ├─ Стратегия C (runt-hang):      %c${result.fixedC.length}%c успех`,
              'font-weight:bold;color:#a72', '');
  console.log(`  ├─ Без runt'а изначально:        %c${result.cleanParagraphs}%c`,
              'font-weight:bold;color:#666', '');
  console.log(`  └─ Остались runt'ы:              %c${result.runtsRemaining.length}%c`,
              'font-weight:bold;color:#c52', '');
  console.log('');

  // ── Часть 3. Сводка по причинам отказа (если детальный лог есть) ──
  if (hasDetailLog) {
    const reasonStats = {
      B: { refused: {}, success: 0 },
      C: { refused: {}, success: 0 }
    };
    for (const entry of detailLog) {
      const s = reasonStats[entry.strategy];
      if (!s) continue;
      if (entry.result === 'success') {
        s.success++;
      } else {
        const r = entry.reason || 'unknown';
        s.refused[r] = (s.refused[r] || 0) + 1;
      }
    }

    console.log('%cПричины отказов (из window.__runtPreventionLog):',
                'font-weight:bold;font-size:1.05em');
    console.log(`  Всего записей в логе: ${detailLog.length}`);
    console.log('');
    console.log(`  B (compression): success=${reasonStats.B.success}, отказы:`);
    for (const [reason, count] of Object.entries(reasonStats.B.refused)) {
      console.log(`    %c${reason}%c: ${count}`, 'font-family:monospace;color:#27a', '');
    }
    if (Object.keys(reasonStats.B.refused).length === 0) console.log('    (нет)');
    console.log(`  C (runt-hang): success=${reasonStats.C.success}, отказы:`);
    for (const [reason, count] of Object.entries(reasonStats.C.refused)) {
      console.log(`    %c${reason}%c: ${count}`, 'font-family:monospace;color:#a72', '');
    }
    if (Object.keys(reasonStats.C.refused).length === 0) console.log('    (нет)');
    console.log('');
  } else {
    console.log('%c⚠ window.__runtPreventionLog не найден.', 'color:#c52');
    console.log('  Чтобы видеть причины отказов, добавь детальное логирование в код (см. спеку, разделы B.3 и C.3).');
    console.log('');
  }

  // ── Часть 4. Детальные таблицы ──
  if (result.fixedC.length > 0) {
    console.groupCollapsed(`%c✓ Стратегия C (runt-hang) — ${result.fixedC.length}`,
                            'color:#a72;font-weight:bold');
    console.table(result.fixedC.map(r => ({
      folio: r.folio, font: r.font, hang: r.hangX, word: r.word, preview: r.preview
    })));
    console.groupEnd();
  }
  if (result.fixedB.length > 0) {
    console.groupCollapsed(`%c✓ Стратегия B (compression) — ${result.fixedB.length}`,
                            'color:#27a;font-weight:bold');
    console.table(result.fixedB.map(r => ({
      folio: r.folio, font: r.font, ws_compressed: r.wsCompressed, preview: r.preview
    })));
    console.groupEnd();
  }
  if (result.runtsRemaining.length > 0) {
    console.groupCollapsed(`%c✗ Остались runt'ы — ${result.runtsRemaining.length}`,
                            'color:#c52;font-weight:bold');
    console.table(result.runtsRemaining.map(r => ({
      folio: r.folio, font: r.font,
      lastWidth_px: r.lastWidth_px, fraction_pct: r.fraction_pct,
      lines: r.lines, preview: r.preview
    })));
    console.groupEnd();
  }

  // ── Часть 5. Если есть детальный лог — таблица всех отказов ──
  if (hasDetailLog) {
    const refusedEntries = detailLog.filter(e => e.result === 'refused');
    if (refusedEntries.length > 0) {
      console.groupCollapsed(`%cДетальный лог отказов — ${refusedEntries.length}`,
                              'color:#888;font-weight:bold');
      console.table(refusedEntries.map(e => {
        const row = {
          strategy: e.strategy,
          reason: e.reason,
          lines: e.lineCount,
          lastW: e.lastLineWidth,
          fraction: e.widthFraction,
          font: e.font || '-',
          preview: e.pPreview
        };
        if (e.strategy === 'C') {
          row.xPx = e.xPx;
          row.limit = e.limit;
          row.targetW = e.targetWidth || '-';
          row.newLines = e.newLineCount || '-';
        } else {
          row.wsCand = e.wsCandidates || '-';
          row.newLines = e.newLineCount || '-';
        }
        return row;
      }));
      console.groupEnd();
    }
  }

  console.log('%cИнтерактивные команды:', 'font-style:italic;color:#888');
  console.log('  %cwindow.__runtDiag.highlight()%c — подсветить категории на странице',
              'font-family:monospace;background:#eee;padding:1px 4px', '');
  console.log('  %cwindow.__runtDiag.scrollTo(N)%c — прокрутить к N-му оставшемуся runt\'у',
              'font-family:monospace;background:#eee;padding:1px 4px', '');
  console.log('  %cwindow.__runtDiag.result%c — сырые данные DOM-анализа',
              'font-family:monospace;background:#eee;padding:1px 4px', '');
  if (hasDetailLog) {
    console.log('  %cwindow.__runtPreventionLog%c — детальный лог решений фазы 0.5',
                'font-family:monospace;background:#eee;padding:1px 4px', '');
  }

  // ── Интерактивные утилиты ──
  window.__runtDiag = {
    result,
    detailLog: hasDetailLog ? detailLog : null,
    highlight() {
      let style = document.getElementById('__runt-diag-style');
      if (!style) {
        style = document.createElement('style');
        style.id = '__runt-diag-style';
        document.head.appendChild(style);
      }
      style.textContent =
        '.__runt-flag-C { outline: 2px dashed #a72 !important; outline-offset: 2px; background: rgba(167,114,34,0.08); }' +
        '.__runt-flag-B { outline: 2px dashed #27a !important; outline-offset: 2px; background: rgba(34,114,167,0.06); }' +
        '.__runt-flag-X { outline: 2px dashed #c52 !important; outline-offset: 2px; background: rgba(204,85,34,0.10); }';
      for (const r of result.fixedC) r.el.classList.add('__runt-flag-C');
      for (const r of result.fixedB) r.el.classList.add('__runt-flag-B');
      for (const r of result.runtsRemaining) r.el.classList.add('__runt-flag-X');
      console.log(
        '%c● C (orange)%c  %c● B (blue)%c  %c● оставшиеся (red)%c — снять: %cwindow.__runtDiag.unhighlight()',
        'color:#a72;font-weight:bold', '',
        'color:#27a;font-weight:bold', '',
        'color:#c52;font-weight:bold', '',
        'font-family:monospace;background:#eee;padding:2px 4px'
      );
    },
    unhighlight() {
      document.querySelectorAll('.__runt-flag-C,.__runt-flag-B,.__runt-flag-X')
        .forEach(el => el.classList.remove('__runt-flag-C', '__runt-flag-B', '__runt-flag-X'));
      const style = document.getElementById('__runt-diag-style');
      if (style) style.remove();
    },
    scrollTo(idx) {
      const r = result.runtsRemaining[idx];
      if (!r) { console.warn('[Runt Diagnostic] нет такого индекса'); return; }
      r.el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      console.log(`[Runt Diagnostic] прокрутка к runt #${idx}: ${r.preview}`);
    }
  };

  console.groupEnd();
})();
