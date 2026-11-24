import { PDFDocument, rgb, PDFName, PDFOperator } from 'pdf-lib';
import fs from 'node:fs/promises';
import zlib from 'node:zlib';

// синтетический PNG 8x10: левая половина красная, правая синяя, верхний ряд зелёный
function makePNG(w, h, px) {
  const raw = Buffer.alloc((w * 3 + 1) * h);
  let o = 0;
  for (let y = 0; y < h; y++) {
    raw[o++] = 0;
    for (let x = 0; x < w; x++) {
      const [r, g, b] = px(x, y);
      raw[o++] = r; raw[o++] = g; raw[o++] = b;
    }
  }
  const idat = zlib.deflateSync(raw);
  const chunks = [];
  const chunk = (type, data) => {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
    const t = Buffer.from(type, 'ascii');
    const crcBuf = Buffer.concat([t, data]);
    const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(crcBuf) >>> 0);
    return Buffer.concat([len, t, data, crc]);
  };
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  chunks.push(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
  chunks.push(chunk('IHDR', ihdr));
  chunks.push(chunk('IDAT', idat));
  chunks.push(chunk('IEND', Buffer.alloc(0)));
  return Buffer.concat(chunks);
}
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

const png = makePNG(8, 10, (x, y) =>
  y === 0 ? [0, 200, 0] : (x < 4 ? [220, 40, 40] : [40, 60, 220]));

const pdf = await PDFDocument.create();
const img = await pdf.embedPng(png);

const N = (v) => v.toFixed(4);
function clipPush(pg, x, y, w, h) {
  const cs = pg.getContentStream();
  cs.push(PDFOperator.of('q'));
  cs.push(PDFOperator.of('re', [N(x), N(y), N(w), N(h)]));
  cs.push(PDFOperator.of('W'));
  cs.push(PDFOperator.of('n'));
}
function clipPop(pg) {
  pg.getContentStream().push(PDFOperator.of('Q'));
}

const bleed = 20, trimW = 200, trimH = 250;
const pg = pdf.addPage([trimW + 2 * bleed, trimH + 2 * bleed]);
const R = { x: bleed, y: bleed, w: trimW, h: trimH };
const M = 200;

// правая полоса — растяжение последнего столбца
clipPush(pg, R.x + R.w, R.y, bleed, R.h);
pg.drawImage(img, { x: R.x + R.w + bleed - R.w * M, y: R.y, width: R.w * M, height: R.h });
clipPop(pg);
// левая
clipPush(pg, R.x - bleed, R.y, bleed, R.h);
pg.drawImage(img, { x: R.x - bleed, y: R.y, width: R.w * M, height: R.h });
clipPop(pg);
// верхняя
clipPush(pg, R.x, R.y + R.h, R.w, bleed);
pg.drawImage(img, { x: R.x, y: R.y + R.h + bleed - R.h * M, width: R.w, height: R.h * M });
clipPop(pg);
// нижняя
clipPush(pg, R.x, R.y - bleed, R.w, bleed);
pg.drawImage(img, { x: R.x, y: R.y - bleed, width: R.w, height: R.h * M });
clipPop(pg);
// угол верх-право
clipPush(pg, R.x + R.w, R.y + R.h, bleed, bleed);
pg.drawImage(img, {
  x: R.x + R.w + bleed - R.w * M, y: R.y + R.h + bleed - R.h * M,
  width: R.w * M, height: R.h * M,
});
clipPop(pg);

pg.drawImage(img, { x: R.x, y: R.y, width: R.w, height: R.h });

pg.node.set(PDFName.of('TrimBox'), pdf.context.obj([R.x, R.y, R.x + R.w, R.y + R.h]));
pg.node.set(PDFName.of('BleedBox'), pdf.context.obj([0, 0, trimW + 2 * bleed, trimH + 2 * bleed]));

await fs.writeFile('/home/claude/proto.pdf', await pdf.save());
console.log('ok');
