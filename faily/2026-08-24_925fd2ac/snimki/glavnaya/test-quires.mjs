// Прогон НАСТОЯЩЕГО пропатченного кода сборки PDF без браузера:
// куски исходника вырезаются по маркерам и исполняются с синтетическими
// фолио. Проверяются размеры листа, боксы, imposition и полосы вылета.
import { PDFDocument, rgb, PDFName, PDFOperator } from 'pdf-lib';
import fs from 'node:fs/promises';
import zlib from 'node:zlib';

const SRC = await fs.readFile('./codex-to-pdf.mjs', 'utf-8');

function slice(from, to) {
  const a = SRC.indexOf(from);
  const b = SRC.indexOf(to, a);
  if (a < 0 || b < 0) throw new Error(`маркер не найден: ${from.slice(0, 50)}`);
  return SRC.slice(a, b);
}

const blockPrelude = slice(
  "  const bleedPt = (cfg.pageSize !== 'a4')",
  '  // Цвет пергамента для bleed-заливки');
const blockHelpers = slice(
  '  // Заливает 4 полосы вылета вокруг trim-rect',
  '  // -------------------------------------------------------------------------\n  // Развёртка folio по PDF-страницам');
const blockFitRect = slice(
  '  function fitRect(f, area) {',
  '  function drawFolioInto(pg, f, imgRef, area) {');
const blockQuires = slice(
  "  if (cfg.pageSize === 'quires') {",
  "  } else if (cfg.pageSize === 'booklet') {");

// ── синтетический PNG: левая половина красная, правая синяя,
//    верхний ряд зелёный, нижний жёлтый — чтобы различать края в вылете
let crcTable = null;
function crc32(buf) {
  if (!crcTable) {
    crcTable = [];
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      crcTable[n] = c >>> 0;
    }
  }
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = crcTable[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function makePNG(w, h, px) {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  let o = 0;
  for (let y = 0; y < h; y++) {
    raw[o++] = 0;
    for (let x = 0; x < w; x++) { const [r, g, b] = px(x, y); raw[o++] = r; raw[o++] = g; raw[o++] = b; }
  }
  const chunk = (type, data) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(Buffer.concat([t, data])) >>> 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2;
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0)),
  ]);
}

// ── контекст, в котором исполняются вырезанные куски ─────────────────────
const PT_PER_MM = 2.83465;
const A4_W = 595.276, A4_H = 841.890, A3_W = 841.890, A3_H = 1190.551;
const A4_LAND_W = A4_H, A4_LAND_H = A4_W, A3_LAND_W = A3_H, A3_LAND_H = A3_W;
const PARCH_COLOR = rgb(204 / 255, 185 / 255, 140 / 255);
const MARK_COLOR = rgb(0, 0, 0);

const argv = Object.fromEntries(process.argv.slice(2).map((s) => {
  const [k, v] = s.split('='); return [k.replace(/^--/, ''), v === undefined ? true : v];
}));

const cfg = {
  pageSize: 'quires', quiresSheet: argv['quires-sheet'] || 'native',
  quiresCoverMode: argv['quires-cover-mode'] || 'separate',
  quiresMarginOuter: null, quiresMarginGutter: 0, quiresMarginVertical: null,
  margin: 10, mode: 'raster', scale: 2, format: 'png', textLayer: false,
  bleed: argv.bleed !== undefined ? parseFloat(argv.bleed) : 5,
  cropMarks: argv['crop-marks'] !== 'false',
  foldMarks: null,
  bleedFill: argv['bleed-fill'] || 'auto',
  carrier: argv.carrier || 'none',
  printFolioWidth: argv['print-folio-width'] ? parseFloat(argv['print-folio-width']) : null,
  printFolioHeight: argv['print-folio-height'] ? parseFloat(argv['print-folio-height']) : null,
};

// 10 листов = 2 обложечных + 8 внутренних (один кватернион) = 20 фолио
const TOTAL_LEAVES = 10;
const quireStructure = { totalLeaves: TOTAL_LEAVES, innerStartLeaf: 2, innerLeafCount: 8, quires: [8] };
const folios = [];
for (let i = 0; i < TOTAL_LEAVES * 2; i++) folios.push({ index: i, width: 620, height: 820, tokens: [] });

const pdf = await PDFDocument.create();
const imgRefs = [];
for (let i = 0; i < folios.length; i++) {
  const png = makePNG(20, 26, (x, y) =>
    y === 0 ? [0, 200, 0] : y === 25 ? [230, 210, 0] : (x < 10 ? [220, 40, 40] : [40, 60, 220]));
  imgRefs.push(await pdf.embedPng(png));
}

// drawFolioInto — упрощённый (без текстового слоя): геометрия та же fitRect
function drawFolioInto(pg, f, imgRef, area) {
  if (!f || !imgRef) return;
  const r = fitRect(f, area);
  pg.drawImage(imgRef, { x: r.x, y: r.y, width: r.w, height: r.h });
}

const evalScope = (code) => (0, eval)(`
  (function(){ ${code}; return { fitRect: typeof fitRect !== 'undefined' ? fitRect : undefined }; })
`);

// Исполняем вырезанные куски в общей области видимости через Function
const run = new Function(
  'cfg', 'folios', 'imgRefs', 'quireStructure', 'pdf', 'PDFName', 'PDFOperator',
  'rgb', 'PT_PER_MM', 'PARCH_COLOR', 'MARK_COLOR',
  'A4_W', 'A4_H', 'A3_W', 'A3_H', 'A4_LAND_W', 'A4_LAND_H', 'A3_LAND_W', 'A3_LAND_H',
  'drawFolioInto', 'console',
  `${blockFitRect}
   ${blockPrelude}
   ${blockHelpers}
   ${blockQuires} }
   return { bleedPt, folioScale, cropMarksEnabled, foldMarksEnabled };`
);

const out = run(cfg, folios, imgRefs, quireStructure, pdf, PDFName, PDFOperator, rgb,
  PT_PER_MM, PARCH_COLOR, MARK_COLOR, A4_W, A4_H, A3_W, A3_H,
  A4_LAND_W, A4_LAND_H, A3_LAND_W, A3_LAND_H, drawFolioInto, console);

console.log('\n— результат —');
console.log('folioScale =', out.folioScale.toFixed(6), ' bleedPt =', out.bleedPt.toFixed(3),
  ' cropMarks =', out.cropMarksEnabled, ' foldMarks =', out.foldMarksEnabled);
const pages = pdf.getPages();
console.log('страниц:', pages.length);
const p0 = pages[0];
const mm = (pt) => (pt / PT_PER_MM).toFixed(2);
console.log('страница:', mm(p0.getWidth()) + '×' + mm(p0.getHeight()), 'мм');
const tb = p0.node.get(PDFName.of('TrimBox'));
const bb = p0.node.get(PDFName.of('BleedBox'));
console.log('TrimBox :', tb ? tb.asArray().map((n) => mm(n.asNumber())).join(', ') : '—');
console.log('BleedBox:', bb ? bb.asArray().map((n) => mm(n.asNumber())).join(', ') : '—');

await fs.writeFile('./test-quires.pdf', await pdf.save());
console.log('→ test-quires.pdf');
