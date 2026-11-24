// ─────────────────────────────────────────────────────────────────────────
// scale-codex.mjs — масштабирование уже собранных листов кодекса БЕЗ
// повторного прогона codex-to-pdf.mjs.
//
// Зачем: пагинация кодекса считается в браузере, и другой Chrome разложит
// строки и абзацы иначе. Поэтому вёрстка берётся готовая — из PDF, — а
// меняется только геометрия страницы: содержимое оборачивается матрицей
// масштаба, боксы (Media/Bleed/Trim) пересчитываются. Ни один символ не
// переезжает относительно соседей.
//
// Что сохраняется в натуральную величину, а что масштабируется:
//   • фолио и всё письмо  — масштабируются (в этом смысл);
//   • вылет               — масштабируется вместе с листом (его полосы
//                           запечены в содержимое, вырезать их нельзя);
//   • КОРЕШОК обложки     — НЕ масштабируется: его ширина задана толщиной
//                           бумаги, а она от формата книги не зависит.
//                           Поэтому обложечный лист собирается из двух
//                           половин по отдельности, с исходным корешком
//                           между ними.
//
// Использование:
//   node scale-codex.mjs --in <dir> --out <dir> [--target-height 189]
//                        [--spine 3.2] [--carrier auto|a4|a3|none]
// ─────────────────────────────────────────────────────────────────────────
import { PDFDocument, PDFName, PDFNumber } from 'pdf-lib';
import fs from 'node:fs/promises';
import path from 'node:path';

const PT_MM = 72 / 25.4;                 // pt в одном мм
const mm = (pt) => pt / PT_MM;
const pt = (v) => v * PT_MM;

const A4  = { w: pt(297), h: pt(210) };  // landscape
const A3  = { w: pt(420), h: pt(297) };  // landscape
const PRINTER_MARGIN = pt(6);            // непечатаемое поле бытового принтера

const argv = Object.fromEntries(process.argv.slice(2).map((s, i, a) => {
  if (!s.startsWith('--')) return [];
  const eq = s.indexOf('=');
  if (eq > 0) return [s.slice(2, eq), s.slice(eq + 1)];
  const next = a[i + 1];
  return [s.slice(2), next && !next.startsWith('--') ? next : true];
}).filter(x => x.length));

const IN  = argv.in  || './codex_aidani';
const OUT = argv.out || './codex_scaled';
const TARGET_H_MM = parseFloat(argv['target-height'] ?? '189');
const SPINE_MM    = parseFloat(argv.spine ?? '3.2');
const CARRIER     = (argv.carrier || 'auto').toLowerCase();
const SRC_FOLIO_H_MM = parseFloat(argv['source-height'] ?? '165');

const k = TARGET_H_MM / SRC_FOLIO_H_MM;

function boxOf(page, name) {
  const arr = page.node.get(PDFName.of(name));
  if (!arr) return null;
  const a = arr.asArray().map(n => n.asNumber());
  return { x0: a[0], y0: a[1], x1: a[2], y1: a[3], w: a[2] - a[0], h: a[3] - a[1] };
}
function setBox(page, name, x0, y0, x1, y1) {
  page.node.set(PDFName.of(name), page.doc.context.obj([x0, y0, x1, y1]));
}

function pickCarrier(contentW, contentH) {
  if (CARRIER === 'none') return null;
  const fits = (s) => contentW <= s.w - 2 * PRINTER_MARGIN && contentH <= s.h - 2 * PRINTER_MARGIN;
  if (CARRIER === 'a4') return A4;
  if (CARRIER === 'a3') return A3;
  if (fits(A4)) return A4;
  if (fits(A3)) return A3;
  return null;
}

// ── обычный лист: одна матрица на всё содержимое ─────────────────────────
async function scalePlain(srcPath, dstPath) {
  const src = await PDFDocument.load(await fs.readFile(srcPath), { updateMetadata: false });
  const pages = src.getPages();
  const report = [];

  for (const page of pages) {
    const trim  = boxOf(page, 'TrimBox');
    const bleed = boxOf(page, 'BleedBox');
    if (!trim) throw new Error('у страницы нет TrimBox — нечего пересчитывать');

    const newTrimW  = trim.w  * k;
    const newTrimH  = trim.h  * k;
    const newBleedW = (bleed ? bleed.w : trim.w) * k;
    const newBleedH = (bleed ? bleed.h : trim.h) * k;

    const carrier = pickCarrier(newBleedW, newBleedH);
    const pageW = carrier ? carrier.w : newBleedW;
    const pageH = carrier ? carrier.h : newBleedH;

    // куда лечь нижнему левому углу блока с вылетом
    const bx = (pageW - newBleedW) / 2;
    const by = (pageH - newBleedH) / 2;
    // источник: тот же угол был в (bleed.x0, bleed.y0) исходных координат
    const sx = bleed ? bleed.x0 : trim.x0;
    const sy = bleed ? bleed.y0 : trim.y0;
    const tx = bx - sx * k;
    const ty = by - sy * k;

    const startRef = src.context.register(
      src.context.flateStream(`q ${k.toFixed(6)} 0 0 ${k.toFixed(6)} ${tx.toFixed(4)} ${ty.toFixed(4)} cm`));
    const endRef = src.context.register(src.context.flateStream('Q'));
    page.node.wrapContentStreams(startRef, endRef);

    page.setSize(pageW, pageH);
    setBox(page, 'MediaBox', 0, 0, pageW, pageH);
    setBox(page, 'CropBox',  0, 0, pageW, pageH);
    setBox(page, 'BleedBox', bx, by, bx + newBleedW, by + newBleedH);
    const trimOffX = (trim.x0 - sx) * k, trimOffY = (trim.y0 - sy) * k;
    setBox(page, 'TrimBox', bx + trimOffX, by + trimOffY,
                            bx + trimOffX + newTrimW, by + trimOffY + newTrimH);
    if (!report.length) report.push({ pageW, pageH, newTrimW, newTrimH, newBleedW, newBleedH, carrier: !!carrier });
  }
  await fs.writeFile(dstPath, await src.save());
  return report[0];
}

// ── обложка: две половины отдельно, корешок в натуральную величину ───────
async function scaleCover(srcPath, dstPath) {
  const src = await PDFDocument.load(await fs.readFile(srcPath), { updateMetadata: false });
  const dst = await PDFDocument.create();
  const pages = src.getPages();
  let report = null;

  for (const page of pages) {
    const trim  = boxOf(page, 'TrimBox');
    const bleed = boxOf(page, 'BleedBox');
    const spineSrc = pt(SPINE_MM);
    const halfW = (trim.w - spineSrc) / 2;          // ширина одной крышки, pt
    const midX  = trim.x0 + trim.w / 2;             // центр корешка в источнике

    const newHalfW = halfW * k;
    const newTrimW = 2 * newHalfW + spineSrc;       // корешок НЕ масштабируется
    const newTrimH = trim.h * k;
    const bleedPtSrc = trim.x0 - bleed.x0;          // вылет в исходнике
    const newBleed = bleedPtSrc * k;
    const newBleedW = newTrimW + 2 * newBleed;
    const newBleedH = newTrimH + 2 * newBleed;

    const carrier = pickCarrier(newBleedW, newBleedH);
    const pageW = carrier ? carrier.w : newBleedW;
    const pageH = carrier ? carrier.h : newBleedH;
    const dp = dst.addPage([pageW, pageH]);

    const bx = (pageW - newBleedW) / 2;
    const by = (pageH - newBleedH) / 2;
    const trimX0 = bx + newBleed, trimY0 = by + newBleed;

    // Клип с заходом на половину корешка: полоса корешка — растянутый
    // пергамент, и небольшое перекрытие половин там незаметно.
    const grab = spineSrc / 2;
    const leftBox  = { left: bleed.x0, bottom: bleed.y0, right: midX + grab, top: bleed.y1 };
    const rightBox = { left: midX - grab, bottom: bleed.y0, right: bleed.x1, top: bleed.y1 };
    const [embL, embR] = await dst.embedPages([page, page], [leftBox, rightBox]);

    // Левая крышка: её левый край трима (trim.x0) → trimX0
    dp.drawPage(embL, { x: trimX0 - trim.x0 * k, y: trimY0 - trim.y0 * k, xScale: k, yScale: k });
    // Правая крышка: её левый край (midX + spineSrc/2) → trimX0 + newHalfW + spineSrc
    dp.drawPage(embR, {
      x: trimX0 + newHalfW + spineSrc - (midX + spineSrc / 2) * k,
      y: trimY0 - trim.y0 * k, xScale: k, yScale: k,
    });

    setBox(dp, 'BleedBox', bx, by, bx + newBleedW, by + newBleedH);
    setBox(dp, 'TrimBox', trimX0, trimY0, trimX0 + newTrimW, trimY0 + newTrimH);
    if (!report) report = { pageW, pageH, newTrimW, newTrimH, newHalfW, carrier: !!carrier };
  }
  await fs.writeFile(dstPath, await dst.save());
  return report;
}

await fs.mkdir(OUT, { recursive: true });
console.log(`масштаб ${k.toFixed(6)} (${SRC_FOLIO_H_MM} → ${TARGET_H_MM} мм по высоте фолио)`);
for (const name of ['quire1.pdf', 'quire2.pdf']) {
  const r = await scalePlain(path.join(IN, name), path.join(OUT, name));
  console.log(`${name}: лист ${mm(r.pageW).toFixed(1)}×${mm(r.pageH).toFixed(1)} мм, ` +
    `трим ${mm(r.newTrimW).toFixed(2)}×${mm(r.newTrimH).toFixed(2)}, ` +
    `с вылетом ${mm(r.newBleedW).toFixed(1)}×${mm(r.newBleedH).toFixed(1)}` +
    (r.carrier ? ', на носителе' : ', без носителя'));
}
const rc = await scaleCover(path.join(IN, 'cover.pdf'), path.join(OUT, 'cover.pdf'));
console.log(`cover.pdf: лист ${mm(rc.pageW).toFixed(1)}×${mm(rc.pageH).toFixed(1)} мм, ` +
  `трим ${mm(rc.newTrimW).toFixed(2)}×${mm(rc.newTrimH).toFixed(2)} ` +
  `(две крышки по ${mm(rc.newHalfW).toFixed(2)} + корешок ${SPINE_MM})`);
