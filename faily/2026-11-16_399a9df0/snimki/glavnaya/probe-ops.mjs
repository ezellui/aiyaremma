// Оценки операций против факта: синтез (форма), перегенерация раздела,
// перегенерация подраздела, добавление раздела (каждое — отдельный план), режим.
// «Факт» — символы, реально ушедшие в симулятор и полученные от него; в деньги
// переводится теми же ставками и тем же CHARS_PER_TOKEN, что у оценщика,
// поэтому разница — это ошибка оценщика в символах, а не разница тарифов.
import { account, sql, sleep, waitStatus } from "../api.mjs";
import { readFileSync, writeFileSync } from "node:fs";
const { CHARS_PER_TOKEN, PRICE_IN, PRICE_OUT } = await import("/home/claude/USER/philosynth/server/services/cost-estimator.ts");
const SIM = "http://127.0.0.1:3927";
const depth = process.argv[2] ?? "standard";
await fetch(SIM + "/__reset", { method: "POST" });
await fetch(SIM + "/__control", { method: "POST", body: JSON.stringify({ stream: { chunk: 6000, intervalMs: 0 } }) });
const usd = (inC, outC) => Math.ceil(inC / CHARS_PER_TOKEN) * PRICE_IN + Math.ceil(outC / CHARS_PER_TOKEN) * PRICE_OUT;
let mark = 0;
async function factSince() {
  const log = (await (await fetch(SIM + "/__log")).json()).filter((e) => e.n > mark);
  let inC = 0, outC = 0;
  for (const e of log) {
    const q = JSON.parse(readFileSync(`/home/claude/lab/prompts/${String(e.n).padStart(4, "0")}.json`, "utf8"));
    const c = q.messages.at(-1).content;
    inC += c.length + (typeof q.system === "string" ? q.system.length : JSON.stringify(q.system ?? "").length);
    outC += e.chars;
  }
  if (log.length) mark = log.at(-1).n;
  return { calls: log.length, inC, outC, usd: usd(inC, outC), keys: log.map((e) => e.keys[0]).join(",") };
}
const rows = [];
const row = (op, est, f) => { rows.push({ op, est, fact: f.usd, calls: f.calls, inC: f.inC, outC: f.outC, keys: f.keys }); console.log(`${op}: оценка $${est?.toFixed(3) ?? "—"} · факт $${f.usd.toFixed(3)} (${f.calls} выз., вход ${f.inC} / выход ${f.outC} симв) ${est ? `· ошибка ${(((est - f.usd) / f.usd) * 100).toFixed(0)}%` : ""}`); };

const A = await account(`ops-${depth}-${Date.now()}@lab.local`);
const lg = await (await fetch(SIM + "/__log")).json(); mark = lg.at(-1)?.n ?? 0;
const body = { seed: "свобода как познанная необходимость", philosophers: ["Спиноза", "Гегель", "Маркс"], sections: ["sum", "graph", "glossary", "theses", "history", "name", "critique", "capsule"], method: "dialectical", depth, synthLevel: "comparative" };
const e = await A.api("POST", "/syntheses/estimate", body);
const r = await A.api("POST", "/syntheses", body); const id = r.json.id;
await waitStatus(id);
row("синтез (8 разделов, форма)", e.json?.cost ?? e.json?.estimate?.cost, await factSince());

async function plan(op, req) {
  const pl = await A.api("POST", `/syntheses/${id}/plans`, req);
  const P = pl.json.plan;
  const g = await A.api("GET", `/syntheses/${id}/plans/${P.id}`);
  const est = g.json.estimatedCost ?? pl.json.estimatedCost;
  await A.api("POST", `/syntheses/${id}/plans/${P.id}/execute`);
  for (let i = 0; i < 120; i++) { const s = (await A.api("GET", `/syntheses/${id}/plans/${P.id}`)).json.plan; if (!s.steps.some((x) => x.status === "confirmed" || x.status === "running")) break; await sleep(500); }
  await sleep(500);
  row(op, est, await factSince());
}
await plan("перегенерация раздела (history)", { regen: ["history"], remove: [], add: [] });
await plan("перегенерация раздела (graph)", { regen: ["graph"], remove: [], add: [] });
await plan("подраздел (critique: Итоговая оценка)", { regen: [], remove: [], add: [], regenSubsections: [{ target: "critique:Итоговая оценка" }] });
await plan("подраздел (theses: Онтологические тезисы)", { regen: [], remove: [], add: [], regenSubsections: [{ target: "theses:Онтологические тезисы" }] });
await plan("добавление раздела (evolution)", { regen: [], remove: [], add: ["evolution"] });

const modes = (await A.api("GET", `/syntheses/${id}/modes`)).json;
const mkey = (modes.modes ?? modes)?.[0]?.key ?? "opponent";
const me = await A.api("GET", `/syntheses/${id}/modes/${mkey}`);
const run = await A.api("POST", `/syntheses/${id}/modes/${mkey}/run`, { param: "Буддийская Абхидхарма" });
for (let i = 0; i < 60; i++) { const lgx = await (await fetch(SIM + "/__log")).json(); if (lgx.at(-1)?.n > mark) { await sleep(1500); break; } await sleep(500); }
row(`режим ${mkey} (run ${run.status})`, me.json?.estimate?.cost, await factSince());
writeFileSync(`/home/claude/lab/cost/ops-${depth}.json`, JSON.stringify(rows, null, 1));
await sql.end(); process.exit(0);
