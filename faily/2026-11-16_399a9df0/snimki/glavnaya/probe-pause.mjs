// Проба оценок модалки паузы против факта.
// 1) концепция с обрывом потока на тезисах → пауза;
// 2) оценки computePauseEstimates с разбивкой вход/выход (повтор его логики);
// 3) для каждого из трёх действий — фактические промпты и ответы симулятора.
// Запуск из клона: node_modules/.bin/tsx /home/claude/lab/cost/probe-pause.mjs <действие: fill|whole|skip>
import { account, sql, sleep, waitStatus } from "../api.mjs";
const R = "/home/claude/USER/philosynth/server";
const { estimateCost, estimateSubsectionCost, CHARS_PER_TOKEN, PRICE_IN, PRICE_OUT } = await import(`${R}/services/cost-estimator.ts`);
const { resolveContextDeps, buildEffectiveDeps } = await import(`${R}/services/synthesis-engine.ts`);
const { buildDynamicOrder } = await import(`${R}/utils/topo-sort.ts`);
const { buildSectionDefs, patchPromptsWithSecCtx, groupPasses } = await import(`${R}/services/section-defs-builder.ts`);
const { buildSYS, baseCtxStatic } = await import(`${R}/services/prompt-builder.ts`);
const { loadActualOutputChars } = await import(`${R}/services/pause-resume-service.ts`);

const action = process.argv[2] ?? "fill";
const SIM = "http://127.0.0.1:3927";
const ctl = (b) => fetch(SIM + "/__control", { method: "POST", body: JSON.stringify(b) });
await fetch(SIM + "/__reset", { method: "POST" });
await ctl({ stream: { chunk: 4000, intervalMs: 0 }, rules: [{ match: "theses", action: "cut", times: 1, fraction: 0.55 }] });

const A = await account(`cost-${action}-${Date.now()}@lab.local`);
const r = await A.api("POST", "/syntheses", { seed: "свобода как познанная необходимость", philosophers: ["Спиноза", "Гегель", "Маркс"], sections: ["sum", "graph", "glossary", "theses", "name", "critique", "capsule"], method: "integrative", depth: "standard", synthLevel: "transformative" });
const id = r.json.id;
console.log("пауза:", await waitStatus(id));
const [{ paused_state: ps }] = await sql`select paused_state from syntheses where id=${id}`;
const g = await A.api("GET", "/syntheses/" + id);
console.log("pauseEstimates сервера:", JSON.stringify(g.json.pauseEstimates ?? g.json.synthesis?.pauseEstimates));

// ── повтор computePauseEstimates с разбивкой ──
const p = { ...ps.genParams, secCtx: { ...(ps.genParams.secCtx ?? {}) } };
const resolved = await resolveContextDeps(p);
const eff = await buildEffectiveDeps(p.sec, resolved, p.generationOrder);
const order = buildDynamicOrder(eff, p.sec, resolved, p.generationOrder).filter(Boolean);
p.sec = order.filter((k) => k !== "sum");
const base = await buildSectionDefs(p); patchPromptsWithSecCtx(base, p.secCtx);
const m = Object.fromEntries(base.map((d) => [d.key, d]));
let n = 1; const defs = order.map((k) => ({ ...m[k], num: n++ }));
const passes = groupPasses(defs);
const est = { depth: p.depth, generationOrder: p.generationOrder, keepFullBudget: p.keepFullBudget };
const sysChars = (await buildSYS(p)).length, baseStaticChars = (await baseCtxStatic(p)).length;
const actual = await loadActualOutputChars(id);
const key = ps.sectionKeys[0];
const fmt = (e) => `вход ${e.inTokens} ток (${Math.round(e.inTokens * CHARS_PER_TOKEN)} симв) · выход ${e.outTokens} ток (${Math.round(e.outTokens * CHARS_PER_TOKEN)} симв) · $${e.cost.toFixed(3)}`;
const whole = await estimateCost({ params: est, passes: [passes.find((x) => x.some((d) => d.key === key))], effectiveDeps: eff, sysChars, baseStaticChars, isEdit: true, actualOutputChars: actual });
console.log(`\nОЦЕНКА «весь раздел» (${key}):`, fmt(whole));
const [meta] = await sql`select metadata from generation_log where synthesis_id=${id} and section_key=${ps.sectionKeys.join("+")} and status='error' order by created_at desc limit 1`;
const detail = meta?.metadata?.subsections ?? [];
const done = new Set(detail.filter((s) => s.status === "done").map((s) => s.name));
const streaming = detail.find((s) => s.status !== "done")?.name;
const missing = [...(streaming ? [streaming] : []), ...(ps.expectedSubsections ?? []).filter((s) => !done.has(s) && s !== streaming)];
console.log("подразделы по генлогу:", detail.map((s) => `${s.name}:${s.status}:${s.chars}`).join(" | "));
console.log("partialSubsections (то, что видит модалка):", JSON.stringify(ps.partialSubsections));
const subSys = (await buildSYS(p, { outputMode: "subsection" })).length;
let fillCost = 0;
for (const s of missing) {
  const e = await estimateSubsectionCost({ sectionKey: key, subsectionName: s, parts: m[key].parts, params: est, sysChars: subSys, baseStaticChars, effectiveDeps: eff, sectionOutputChars: actual[key], actualOutputChars: actual });
  fillCost += e.cost; console.log(`ОЦЕНКА подраздела «${s}»:`, fmt(e));
}
console.log(`ОЦЕНКА «догенерировать» итого: $${fillCost.toFixed(3)}`);
const skip = await estimateCost({ params: est, passes: passes.slice(ps.passIdx + 1), effectiveDeps: eff, sysChars, baseStaticChars, isEdit: true, actualOutputChars: actual });
console.log(`ОЦЕНКА «далее» (${passes.slice(ps.passIdx + 1).map((x) => x.map((d) => d.key).join("+")).join(", ")}):`, fmt(skip));

// ── исполнение выбранного действия и факт ──
const before = (await (await fetch(SIM + "/__log")).json()).length;
const body = action === "fill" ? { mode: "fill-missing-subs" } : action === "whole" ? { mode: "retry" } : { mode: "skip" };
const rs = await A.api("POST", `/syntheses/${id}/resume`, body);
console.log(`\nresume ${JSON.stringify(body)} →`, rs.status, rs.text.slice(0, 160));
await sleep(500); await waitStatus(id, (s) => s !== "generating", 180000);
const log = (await (await fetch(SIM + "/__log")).json()).slice(before);
const { readFileSync } = await import("node:fs");
let inC = 0, outC = 0;
for (const e of log) {
  const req = JSON.parse(readFileSync(`/home/claude/lab/prompts/${String(e.n).padStart(4, "0")}.json`, "utf8"));
  const c = req.messages.at(-1).content; const sl = typeof req.system === "string" ? req.system.length : JSON.stringify(req.system ?? "").length;
  inC += c.length + sl; outC += e.chars;
  console.log(`ФАКТ вызов ${e.n} [${e.keys.join("+")}]: вход ${c.length + sl} симв · выход ${e.chars} симв`);
}
const inT = Math.ceil(inC / CHARS_PER_TOKEN), outT = Math.ceil(outC / CHARS_PER_TOKEN);
console.log(`ФАКТ «${action}» итого: ${log.length} вызов(ов) · вход ${inC} симв · выход ${outC} симв · по тем же ценам $${(inT * PRICE_IN + outT * PRICE_OUT).toFixed(3)} (вход $${(inT * PRICE_IN).toFixed(3)}, выход $${(outT * PRICE_OUT).toFixed(3)})`);
await sql.end(); process.exit(0);
