/**
 * claude-sim — симулятор Anthropic Messages API (SSE) для стенда PhiloSynth.
 *
 * Отвечает на запросы генерации разделов, собирая ответ из настоящего
 * корпуса — файла-образца концепции (sample/…html): раздел за разделом,
 * секция за секцией по точным именам data-section из ЗАДАНИЯ. Секции, которых
 * в образце нет, дописываются по указаниям промпта (столбцы таблиц — из
 * «Столбцы: …» / «Таблица: …» самого задания). Имена участников образца
 * подменяются участниками синтеза (склонение простое).
 *
 * Управление сценариями — HTTP-ручки самого мока:
 *   POST /__control  {rules:[{match, action, times, after, delayMs}], stream:{chunk, intervalMs}}
 *       match  — ключ раздела (graph, theses…) | "mode" | "other" | "*" | подстрока промпта
 *       action — billing | overloaded | auth | cut (обрыв посреди стрима) |
 *                max_tokens (stop_reason=max_tokens) | slow (delayMs перед ответом) | hang
 *   POST /__reset   — снять правила
 *   GET  /__log     — журнал вызовов (что спрошено, что отвечено)
 * Метки в зерне концепции тоже работают: [SIM:billing:graph], [SIM:cut:theses].
 *
 * Запуск: node claude-sim.mjs [порт=3927] [путь к образцу]
 */
import http from "node:http";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";

const PORT = +(process.argv[2] ?? 3927);
const SAMPLE = process.argv[3] ?? "/home/claude/USER/philosynth/sample/PS-6933-6RIK-vmeschayuschiy-razlom-rgG2.html";
const DUMP = process.env.SIM_DUMP ?? "/home/claude/lab/prompts";
mkdirSync(DUMP, { recursive: true });

/* ── Корпус ──────────────────────────────────────────────────────────── */
const src = readFileSync(SAMPLE, "utf8");
function divEnd(s, start) {
  const re = /<div\b|<\/div>/g; re.lastIndex = start; let depth = 0, m;
  while ((m = re.exec(s))) { depth += m[0] === "</div>" ? -1 : 1; if (depth === 0) return m.index + 6; }
  return s.length;
}
const TITLE_KEYS = [
  [/резюме/i, "sum"], [/граф/i, "graph"], [/глоссарий/i, "glossary"], [/тезис/i, "theses"],
  [/назван/i, "name"], [/историческ/i, "history"], [/происхожд/i, "origin"], [/практическ/i, "practical"],
  [/диалог/i, "dialogue"], [/эволюц/i, "evolution"], [/критическ/i, "critique"], [/капсул/i, "capsule"],
];
const keyOfTitle = (t) => TITLE_KEYS.find(([re]) => re.test(t))?.[1] ?? null;
const LIB = {}; // key → { title, subs: Map(name → html) }
for (let i = src.indexOf('<div class="doc-section">'); i >= 0; i = src.indexOf('<div class="doc-section">', i + 10)) {
  const end = divEnd(src, i), block = src.slice(i, end);
  const title = (block.match(/<div class="section-title">([\s\S]*?)<\/div>/)?.[1] ?? "").trim();
  const key = keyOfTitle(title); if (!key || LIB[key]) continue;
  const subs = new Map();
  for (let j = block.indexOf("<div data-section="); j >= 0; ) {
    const e = divEnd(block, j), name = block.slice(j).match(/data-section="([^"]+)"/)[1];
    if (!subs.has(name)) subs.set(name, block.slice(j, e));
    j = block.indexOf("<div data-section=", e);
  }
  LIB[key] = { title, subs };
}
{
  const a = paras(LIB.sum?.subs.get("Цели и метод")), b = paras(LIB.critique?.subs.get("Итоговая оценка"));
  const trim = (p) => { const t = p.replace(/<[^>]+>/g, ""); return `<p>${t.length > 650 ? t.slice(0, t.lastIndexOf(".", 650) + 1) : t}</p>`; };
  if (a.length >= 2) capsuleSrc = [a[0], a[1], b[0] ?? a[2]].filter(Boolean).map(trim).join("\n");
}
// Капсулы в образце нет — три абзаца собираются из «Цели и метод» резюме и «Итоговая оценка» критики
const paras = (h) => [...(h ?? "").matchAll(/<p>([\s\S]*?)<\/p>/g)].map((m) => m[0]).filter((p) => p.replace(/<[^>]+>/g, "").length > 200);
let capsuleSrc = null;
const ALIASES = { "Портрет каждого философа": "Портрет каждого участника синтеза", "Капсула": null };
const CONCEPT_NAME = "Вмещающий разлом";
// Категории графа образца — для правдоподобных дописанных таблиц
const CATS = [...(LIB.graph?.subs.get("Таблица категорий") ?? "").matchAll(/<tr>\s*<td>([\s\S]*?)<\/td>/g)].map((m) => m[1].replace(/<[^>]+>/g, "").trim()).filter(Boolean);

/* ── Подмена участников ───────────────────────────────────────────────── */
function forms(n) {
  if (/[ьй]$/.test(n)) { const b = n.slice(0, -1); return [n, b + "я", b + "ю", b + "ем", b + "е"]; }
  if (/а$/.test(n)) { const b = n.slice(0, -1); return [n, b + "ы", b + "е", b + "ой", b + "е"]; }
  if (/[оеиуюэы]$/.test(n)) return [n, n, n, n, n];
  return [n, n + "а", n + "у", n + "ом", n + "е"];
}
const JUNG = ["Юнг", "Юнга", "Юнгу", "Юнгом", "Юнге"];
function personalize(html, ctx) {
  let h = html;
  if (ctx.phils[0]) {
    const f = forms(ctx.phils[0].split(/\s+/).pop());
    h = h.replace(/Карл Густав Юнг/g, ctx.phils[0]).replace(/Юнг(ом|а|у|е)?(?![а-яё])/g, (m, e) => f[JUNG.indexOf("Юнг" + (e ?? ""))]);
    h = h.replace(/юнгианск/gi, (m) => (m[0] === "Ю" ? "Ф" : "ф") + "илософск");
  }
  if (ctx.phils[1]) h = h.replace(/Грамматик[аиеуой]* самоотрицания/g, ctx.phils[1]);
  if (ctx.title) h = h.split(CONCEPT_NAME).join(ctx.title);
  return h;
}

/* ── Разбор задания ───────────────────────────────────────────────────── */
function parseTask(prompt) {
  const ti = prompt.lastIndexOf("ЗАДАНИЕ"); if (ti < 0) return null;
  const task = prompt.slice(ti);
  const heads = [...task.matchAll(/^§ (\d+) — ([^\n]+)$/gm)];
  if (!heads.length) return null;
  return heads.map((h, i) => {
    const body = task.slice(h.index, heads[i + 1]?.index ?? task.length);
    const subs = []; const descr = {};
    const re = /^«([^»\n]{2,90})»\s*\n([\s\S]*?)(?=^«[^»\n]{2,90}»\s*\n|^ТРЕБОВАНИЯ:|$(?![\s\S]))/gm;
    for (const m of body.matchAll(re)) if (!subs.includes(m[1])) { subs.push(m[1]); descr[m[1]] = m[2]; }
    return { num: +h[1], title: h[2].trim(), key: keyOfTitle(h[2]), subs, descr };
  });
}
function paramsOf(prompt) {
  const phils = (prompt.match(/ФИЛОСОФЫ: ([^\n]+)/)?.[1] ?? "").split(",").map((s) => s.trim()).filter((s) => s && s !== "—");
  const seed = prompt.match(/ЗЕРНО КОНЦЕПЦИИ: «([^»]*)»/)?.[1] ?? "";
  const title = prompt.match(/### Название концепции\n([^\n]+)/)?.[1]?.replace(/<[^>]+>/g, "").trim();
  return { phils, seed, title: title && title.length < 80 && title !== "заглушка" ? title : null };
}
const cap = (s) => s.charAt(0) + s.slice(1).toLowerCase();

function hash(s) { let h = 2166136261; for (const c of s) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }
function rnd(seed) { let x = hash(seed) || 1; return () => ((x = Math.imul(x ^ (x >>> 15), 2246822507) ^ Math.imul(x ^ (x >>> 13), 3266489909)), (x >>> 0) / 4294967296); }

function writtenTable(cols, seed) {
  const r = rnd(seed), rows = [];
  for (let i = 0; i < 4; i++) rows.push(cols.map((c, j) => {
    if (/оценка|сила|степень|центральн|определённ|(0[–-]1)/i.test(c)) return (0.4 + r() * 0.55).toFixed(2);
    if (/приоритет|риск/i.test(c)) return ["высокий", "средний", "низкий"][Math.floor(r() * 3)];
    if (j === 0) return CATS[Math.floor(r() * CATS.length)] ?? `Пункт ${i + 1}`;
    return `${c.toLowerCase()}: ${["уточнить по §2", "держится на категории «" + (CATS[i] ?? "разлом") + "»", "согласовано с §4", "требует проверки"][Math.floor(r() * 4)]}`;
  }));
  return `<table class="doc-table"><thead><tr>${cols.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>${rows.map((rr) => `<tr>${rr.map((x) => `<td>${x}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
}
function writtenSub(name, descr, ctx) {
  const colsM = descr.match(/(?:Столбцы(?: таблицы)?|Таблица):\s*([^\n.]+)/);
  const cols = colsM ? colsM[1].split("|").map((s) => s.trim()).filter(Boolean) : null;
  const gist = descr.replace(/\s+/g, " ").trim().slice(0, 260);
  const p1 = `<p>Секция «${name}» составлена симулятором по заданию: ${gist}${gist.length >= 260 ? "…" : ""}</p>`;
  const p2 = `<p>Опора — категории графа (§2): ${CATS.slice(0, 4).map((c) => `«${c}»`).join(", ")}${ctx.phils.length ? `; участники — ${ctx.phils.join(", ")}` : ""}.</p>`;
  return `<div data-section="${name}">\n<h4>${name}</h4>\n${p1}\n${cols && cols.length > 1 && cols.length < 10 ? writtenTable(cols, name + ctx.seed) : ""}\n${p2}\n</div>`;
}
function composeSection(sec, ctx, stats) {
  const lib = LIB[sec.key];
  const parts = sec.subs.map((name) => {
    if (sec.key === "capsule" && capsuleSrc) { stats.corpus++; return `<div data-section="${name}">\n<h4>${name}</h4>\n${capsuleSrc}\n</div>`; }
    const html = lib?.subs.get(name) ?? lib?.subs.get(ALIASES[name] ?? "");
    if (html) { stats.corpus++; return html.replace(/data-section="[^"]+"/, `data-section="${name}"`).replace(/<h4>[^<]*<\/h4>/, `<h4>${name}</h4>`); }
    stats.written++; return writtenSub(name, sec.descr[name] ?? "", ctx);
  });
  if (!sec.subs.length && lib) for (const h of lib.subs.values()) { stats.corpus++; parts.push(h); }
  return `<div class="doc-section">\n<div class="section-num">§ ${sec.num}</div>\n<div class="section-title">${cap(sec.title)}</div>\n<div class="doc-content">\n\n${parts.map((p) => personalize(p, ctx)).join("\n\n")}\n\n</div>\n</div>`;
}

/* ── Прочие задания (режимы, обогащение, преобразование, переименование…) ── */
function otherAnswer(prompt, system) {
  const ctx = paramsOf(prompt);
  if (/json/i.test(prompt.slice(-1500)) && /\{[\s\S]*\}/.test(prompt.slice(-1500))) {
    return { kind: "json", text: JSON.stringify({ title: ctx.title ?? "Симулированное название", value: 0.7, justification: "Ответ симулятора: значение выбрано по признакам категории в §2 и §3." }) };
  }
  const sec = (prompt.slice(-4000).match(/§ ?(\d+)/) ?? [])[1] ?? "1";
  const body = [...(LIB.critique?.subs.values() ?? [])][0] ?? "<p>…</p>";
  return { kind: "other", text: `<div class="doc-section">\n<div class="section-num">§ ${sec}</div>\n<div class="section-title">Ответ симулятора</div>\n<div class="doc-content">\n${personalize(body, ctx)}\n</div>\n</div>` };
}

/* ── Сценарии ─────────────────────────────────────────────────────────── */
let rules = [], streamCfg = { chunk: 600, intervalMs: 25 };
const log = [];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function pickRule(keys, prompt) {
  const seedRule = prompt.match(/\[SIM:([a-z_]+):([a-z*]+)\]/);
  const all = [...rules];
  if (seedRule) all.push({ match: seedRule[2], action: seedRule[1], times: 1, _seed: seedRule[0] + (paramsOf(prompt).seed) });
  for (const r of all) {
    const hit = r.match === "*" || keys.includes(r.match) || (r.match.length > 12 && prompt.includes(r.match));
    if (!hit) continue;
    r.seen = (r.seen ?? 0) + 1;
    if (r.after && r.seen <= r.after) continue;
    if (r._seed) { if (fired.has(r._seed)) continue; fired.add(r._seed); return r; }
    if (r.times !== undefined) { if ((r.used ?? 0) >= r.times) continue; r.used = (r.used ?? 0) + 1; }
    return r;
  }
  return null;
}
const fired = new Set();
const ERR = {
  billing: [400, "invalid_request_error", "Your credit balance is too low to access the Anthropic API."],
  overloaded: [529, "overloaded_error", "Overloaded"],
  auth: [401, "authentication_error", "invalid x-api-key"],
};

let n = 0;
http.createServer((req, res) => {
  let body = "";
  req.on("data", (d) => (body += d));
  req.on("end", async () => {
    const url = req.url ?? "";
    if (url.startsWith("/__control")) { const c = JSON.parse(body || "{}"); if (c.rules) rules = c.rules; if (c.stream) streamCfg = { ...streamCfg, ...c.stream }; res.end(JSON.stringify({ ok: true, rules, streamCfg })); return; }
    if (url.startsWith("/__reset")) { rules = []; streamCfg = { chunk: 600, intervalMs: 25 }; res.end('{"ok":true}'); return; }
    if (url.startsWith("/__log")) { res.setHeader("content-type", "application/json"); res.end(JSON.stringify(log)); return; }
    n++;
    let reqJ = {}; try { reqJ = JSON.parse(body); } catch {}
    const c = reqJ.messages?.at(-1)?.content; const prompt = typeof c === "string" ? c : JSON.stringify(c ?? "");
    writeFileSync(`${DUMP}/${String(n).padStart(4, "0")}.json`, body);
    const secs = parseTask(prompt); const ctx = paramsOf(prompt);
    const stats = { corpus: 0, written: 0 };
    let text, keys;
    if (secs) { keys = secs.map((s) => s.key ?? "?"); text = secs.map((s) => composeSection(s, ctx, stats)).join("\n\n"); }
    else { const o = otherAnswer(prompt, reqJ.system); keys = [o.kind === "json" ? "json" : "other", "mode"]; text = o.text; }
    const rule = pickRule(keys, prompt);
    const entry = { n, at: new Date().toISOString(), keys, subs: secs?.map((s) => s.subs.length), ...stats, chars: text.length, rule: rule?.action ?? null, stream: !!reqJ.stream };
    log.push(entry); console.log(JSON.stringify(entry));
    if (rule?.action === "slow" || rule?.action === "hang") await sleep(rule.action === "hang" ? 3_600_000 : rule.delayMs ?? 8000);
    if (rule && ERR[rule.action]) { const [st, type, message] = ERR[rule.action]; res.writeHead(st, { "content-type": "application/json" }); res.end(JSON.stringify({ type: "error", error: { type, message } })); return; }
    const outTok = Math.round(text.length / 3.2), inTok = Math.round(prompt.length / 3.2 + (reqJ.system?.length ?? 0) / 3.2);
    if (!reqJ.stream) { res.writeHead(200, { "content-type": "application/json" }); res.end(JSON.stringify({ id: "msg_sim_" + n, type: "message", role: "assistant", content: [{ type: "text", text }], stop_reason: "end_turn", usage: { input_tokens: inTok, output_tokens: outTok } })); return; }
    res.writeHead(200, { "content-type": "text/event-stream" });
    const send = (o) => res.write(`event: ${o.type}\ndata: ${JSON.stringify(o)}\n\n`);
    send({ type: "message_start", message: { id: "msg_sim_" + n, usage: { input_tokens: inTok, output_tokens: 1 } } });
    send({ type: "content_block_start", index: 0, content_block: { type: "text", text: "" } });
    const limit = rule?.action === "cut" || rule?.action === "max_tokens" ? Math.floor(text.length * (rule.fraction ?? 0.45)) : text.length;
    for (let i = 0; i < limit; i += streamCfg.chunk) {
      send({ type: "content_block_delta", index: 0, delta: { type: "text_delta", text: text.slice(i, Math.min(i + streamCfg.chunk, limit)) } });
      if (streamCfg.intervalMs) await sleep(streamCfg.intervalMs);
    }
    if (rule?.action === "cut") { res.destroy(); return; }
    send({ type: "content_block_stop", index: 0 });
    send({ type: "message_delta", delta: { stop_reason: rule?.action === "max_tokens" ? "max_tokens" : "end_turn" }, usage: { output_tokens: rule?.action === "max_tokens" ? Math.round(limit / 3.2) : outTok } });
    send({ type: "message_stop" });
    res.end();
  });
}).listen(PORT, "127.0.0.1", () => console.log(`claude-sim :${PORT}; корпус: ${Object.entries(LIB).map(([k, v]) => k + "/" + v.subs.size).join(" ")}; категорий ${CATS.length}; капсула ${capsuleSrc ? "есть" : "нет"}`));
