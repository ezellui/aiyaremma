// Одновременные генерации: N пользователей запускают по синтезу, у каждого открыт WS.
// Поток симулятора — как у настоящей модели (≈ 200 симв./с дельтами по ~24 симв.).
// Снимаем: CPU/RSS сервера, CPU симулятора и PG, задержку /health и GET документа,
// поток WS-сообщений, ошибки. Запуск: tsx gen.mjs N [окно_с] [chunk] [intervalMs]
import { readFileSync, readdirSync } from "node:fs";
import WebSocket from "/home/claude/lab/stress/node_modules/ws/index.js";
import { account, sql, sleep } from "../api.mjs";
const API = "http://127.0.0.1:3000/api/v1", SIM = "http://127.0.0.1:3927";
const N = Number(process.argv[2] ?? 10), WIN = Number(process.argv[3] ?? 60);
const CHUNK = Number(process.argv[4] ?? 24), IVL = Number(process.argv[5] ?? 120);
const pidsOf = (re) => readdirSync("/proc").filter((p) => /^\d+$/.test(p)).filter((p) => { try { return re.test(readFileSync(`/proc/${p}/cmdline`, "utf8").replace(/\0/g, " ")); } catch { return false; } });
const ticks = (pids) => pids.reduce((s, p) => { try { const f = readFileSync(`/proc/${p}/stat`, "utf8").split(") ")[1].split(" "); return s + Number(f[11]) + Number(f[12]); } catch { return s; } }, 0);
const rssMb = (pids) => pids.reduce((s, p) => { try { return s + Number(/VmRSS:\s+(\d+)/.exec(readFileSync(`/proc/${p}/status`, "utf8"))[1]); } catch { return s; } }, 0) / 1024;
const srv = pidsOf(/node --import tsx index\.ts/), sim = pidsOf(/claude-sim\.mjs/);
const pg = () => pidsOf(/^postgres/);
const pct = (a, q) => { if (!a.length) return NaN; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(q * s.length))]; };

const users = [];
for (let i = 0; i < N; i++) users.push(await account(`stress${i}@lab.local`, "password-lab", `Нагрузка ${i}`));
const ids = Object.fromEntries((await sql`select k, v from lab_ids`).map((r) => [r.k, r.v]));
await fetch(SIM + "/__reset", { method: "POST" });
await fetch(SIM + "/__control", { method: "POST", body: JSON.stringify({ stream: { chunk: CHUNK, intervalMs: IVL } }) });

// WS у каждого
let wsMsgs = 0, wsBytes = 0, wsDeltas = 0, wsErrors = 0, sectionsDone = 0;
const sockets = await Promise.all(users.map((u) => new Promise((res) => {
  const ws = new WebSocket("ws://127.0.0.1:3000/ws", { headers: { cookie: u.cookie } });
  ws.on("message", (d) => { wsMsgs++; wsBytes += d.length; const s = d.toString(); if (s.includes('"stream_delta"')) wsDeltas++; else if (s.includes('"section_done"')) sectionsDone++; else if (s.includes('"stream_error"')) wsErrors++; });
  ws.on("open", () => res(ws)); ws.on("error", () => { wsErrors++; res(ws); });
})));

const body = { seed: "свобода как познанная необходимость", philosophers: ["Спиноза", "Гегель", "Маркс"], sections: ["sum", "graph", "glossary", "theses", "history", "name", "critique", "capsule"], method: "dialectical", depth: "standard", synthLevel: "comparative" };
const t0s = ticks(srv), t0m = ticks(sim), t0p = ticks(pg()), w0 = Date.now();
const started = await Promise.all(users.map((u) => u.api("POST", "/syntheses", body)));
const startMs = Date.now() - w0;
const sids = started.map((r) => r.json?.id).filter(Boolean);
const startErr = started.filter((r) => r.status >= 300).map((r) => r.status + " " + (r.json?.code ?? ""));
// после старта — окно наблюдения
await sleep(3000);
const hLat = [], dLat = [], rssS = [];
const W0 = Date.now(), c0s = ticks(srv), c0m = ticks(sim), c0p = ticks(pg()), m0 = wsMsgs, b0 = wsBytes, d0 = wsDeltas;
let stop = false;
const probeHealth = (async () => { while (!stop) { const t = performance.now(); await fetch(API + "/health").catch(() => {}); hLat.push(performance.now() - t); await sleep(200); } })();
const probeDoc = (async () => { while (!stop) { const t = performance.now(); await fetch(API + "/syntheses/" + ids.s2, { headers: { cookie: users[0].cookie } }).catch(() => {}); dLat.push(performance.now() - t); rssS.push(rssMb(srv)); await sleep(1000); } })();
await sleep(WIN * 1000);
stop = true; await probeHealth; await probeDoc;
const secs = (Date.now() - W0) / 1000;
const cpu = (a, b) => Math.round(((a - b) / 100 / secs) * 100);
const [{ n: pgConns }] = await sql`select count(*)::int n from pg_stat_activity where datname='philosynth'`;
const res = {
  N, startMs, startErr: startErr.length ? startErr.slice(0, 3) : 0,
  "CPU сервера %": cpu(ticks(srv), c0s), "CPU симулятора %": cpu(ticks(sim), c0m), "CPU PG %": cpu(ticks(pg()), c0p),
  "RSS сервера МБ": Math.round(Math.max(...rssS)),
  "health p50/p99 мс": `${pct(hLat, 0.5).toFixed(0)}/${pct(hLat, 0.99).toFixed(0)}`,
  "документ p50/p99 мс": `${pct(dLat, 0.5).toFixed(0)}/${pct(dLat, 0.99).toFixed(0)}`,
  "WS сообщ./с": Math.round((wsMsgs - m0) / secs), "дельт/с": Math.round((wsDeltas - d0) / secs), "WS КБ/с": Math.round((wsBytes - b0) / 1024 / secs),
  "ожидалось дельт/с": Math.round(sids.length * 1000 / IVL), "разделов готово": sectionsDone, "ошибок WS": wsErrors, "соединений PG": pgConns,
};
console.log(JSON.stringify(res));
// отмена
for (let i = 0; i < sockets.length; i++) if (sids[i]) sockets[i].send(JSON.stringify({ type: "cancel", synthesisId: sids[i] }));
await sleep(3000);
for (const s of sockets) s.close();
await sql.end(); process.exit(0);
