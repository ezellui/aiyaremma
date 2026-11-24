/**
 * Обход родословной — ОДНА функция (беседа 18.3, долг Д-88).
 *
 * До 18.3 «философов по всей родословной» считали два одинаковых обхода
 * (`searchByPhilosophers` у `/lineage/search`, 3.1, и `ANC_CTE` фильтра
 * поиска, 18.1), и оба шли только по строкам `synthesis_lineage`. Дерево
 * импортированного файла (`syntheses.file_genealogy`) в строки попадает
 * лишь верхним уровнем (импорт 4.3), так что философы ВЛОЖЕННЫХ
 * узлов-концепций файла обходу были не видны: импортированный мета-синтез
 * не находился по философу своего «файлового» предка. Похожим концепциям
 * (18.3) тот же обход нужен в третий раз — он сведён сюда.
 *
 * `lineageWalkCte(roots?)` отдаёт рекурсивный CTE `walk` — все предки
 * каждого корня, транзитивно, глубина ≤ 10 (тот же предел, что был):
 *   root_id — концепция, чья родословная обходится;
 *   kind    — 'philosopher' | 'concept';
 *   sid     — id концепции-предка, у которой есть строка в БД; NULL — узел
 *             дерева файла (снимок) либо философ;
 *   node    — узел дерева файла (jsonb); NULL — предок из строки БД;
 *   name    — имя философа либо имя узла файла; у концепции из БД — NULL
 *             (название даёт JOIN с syntheses, как всюду с 8.5);
 *   depth   — 0 у самого корня, 1 у прямых родителей.
 *
 * ПРАВИЛО ПРИОРИТЕТА 15.1 — то же, что у `getAncestors`
 * (`unlinkedFileParents`): действующая строка `synthesis_lineage` на
 * позиции i перекрывает узел файла с индексом i; узел файла виден только
 * там, где связи нет или её родитель удалён (SET NULL). Ниже узла файла
 * идут его собственные `participants` — у снимка строк в БД нет.
 *
 * Потребители — три, и все берут обход отсюда (сторож 5ba сверяет, что
 * они дают один ответ):
 *   1) `searchByPhilosophers` (lineage-service) — `GET /lineage/search`;
 *   2) фильтр поиска `philArea=lineage` и `epoch` в этой области
 *      (services/search.ts);
 *   3) признаки сходства «философы по родословной» и «род» (общие предки)
 *      — services/similarity.ts.
 *
 * Модуль-лист: импортирует только db. Доступ не проверяет — это дело
 * потребителей (как у lineage-service).
 */
import type postgres from "postgres";

import { sql } from "../db/index.js";

type SqlFragment = postgres.PendingQuery<postgres.Row[]>;

/** Предел глубины обхода — как у CTE 02 §2.4 и `getAncestors`. */
export const LINEAGE_WALK_MAX_DEPTH = 10;

/**
 * Действующая строка родословной: философ с именем либо концепция с живым
 * родителем (SQL-вид `rowIsLive` lineage-service). Рассчитана на
 * `synthesis_lineage l`.
 */
export const LIVE_LINEAGE_ROW_SQL = sql`((l.parent_type = 'philosopher' AND coalesce(l.parent_name, '') <> '') OR (l.parent_type = 'synthesis' AND l.parent_synthesis_id IS NOT NULL))`;

/** Участники узла дерева файла массивом (чего бы там ни лежало). */
const participantsOf = (node: SqlFragment): SqlFragment =>
  sql`CASE WHEN jsonb_typeof(${node} -> 'participants') = 'array' THEN ${node} -> 'participants' ELSE '[]'::jsonb END`;

/** Вид узла файла: всё, что не философ, — концепция (как sanitizeFileGenealogy). */
const FILE_NODE_KIND = sql`CASE WHEN fp.node ->> 'type' = 'philosopher' THEN 'philosopher' ELSE 'concept' END`;

/**
 * CTE `walk` — обход родословной (см. шапку). `roots` — условие на
 * `syntheses s`, какие концепции взять корнями; без него — все.
 * Вставляется после `WITH RECURSIVE`.
 */
export function lineageWalkCte(roots?: SqlFragment): SqlFragment {
  return sql`walk AS (
    SELECT s.id AS root_id, 'concept'::text AS kind, s.id AS sid, NULL::jsonb AS node,
           NULL::text AS name, 0 AS depth
    FROM syntheses s
    WHERE ${roots ?? sql`true`}

    UNION ALL

    SELECT w.root_id, p.kind, p.sid, p.node, p.name, w.depth + 1
    FROM walk w
    CROSS JOIN LATERAL (
      -- (а) действующие строки БД концепции-предка
      SELECT CASE WHEN l.parent_type = 'philosopher' THEN 'philosopher' ELSE 'concept' END AS kind,
             l.parent_synthesis_id AS sid, NULL::jsonb AS node,
             CASE WHEN l.parent_type = 'philosopher' THEN l.parent_name END AS name
      FROM synthesis_lineage l
      WHERE w.sid IS NOT NULL AND l.synthesis_id = w.sid AND ${LIVE_LINEAGE_ROW_SQL}

      UNION ALL

      -- (б) узлы верхнего уровня дерева файла той же концепции, не перекрытые
      --     действующей строкой на своей позиции (правило приоритета 15.1)
      SELECT ${FILE_NODE_KIND}, NULL::uuid, fp.node, fp.node ->> 'name'
      FROM syntheses fs
      CROSS JOIN LATERAL jsonb_array_elements(${participantsOf(sql`fs.file_genealogy`)})
        WITH ORDINALITY AS fp(node, ord)
      WHERE w.sid IS NOT NULL AND fs.id = w.sid
        AND NOT EXISTS (
          SELECT 1 FROM synthesis_lineage l
          WHERE l.synthesis_id = w.sid AND l.position = fp.ord - 1 AND ${LIVE_LINEAGE_ROW_SQL})

      UNION ALL

      -- (в) вложенные узлы узла файла: у снимка строк в БД нет
      SELECT ${FILE_NODE_KIND}, NULL::uuid, fp.node, fp.node ->> 'name'
      FROM jsonb_array_elements(
             CASE WHEN w.sid IS NULL AND w.node IS NOT NULL THEN ${participantsOf(sql`w.node`)} ELSE '[]'::jsonb END
           ) AS fp(node)
    ) p
    WHERE w.kind = 'concept' AND w.depth < ${LINEAGE_WALK_MAX_DEPTH}
  )`;
}

/**
 * Условие «в родословной концепции `s` есть названные философы» поверх CTE
 * `walk` (корни — все): `all` — все названные, `any` — любой. Имена —
 * непустой список без повторов.
 */
export function lineagePhilosophersCond(names: readonly string[], mode: "all" | "any"): SqlFragment {
  const having =
    mode === "all" ? sql`count(DISTINCT w.name) = ${names.length}` : sql`count(DISTINCT w.name) >= 1`;
  return sql`s.id IN (
    SELECT w.root_id FROM walk w
    WHERE w.kind = 'philosopher' AND w.name IN ${sql([...names])}
    GROUP BY w.root_id HAVING ${having})`;
}

/** id концепций, в родословной которых есть ВСЕ названные философы. */
export async function rootsWithAllPhilosophers(names: readonly string[]): Promise<string[]> {
  if (names.length === 0) return [];
  const rows = await sql<{ id: string }[]>`
    WITH RECURSIVE ${lineageWalkCte()}
    SELECT s.id FROM syntheses s WHERE ${lineagePhilosophersCond(names, "all")}`;
  return rows.map((r) => r.id);
}

/** Строка обхода для потребителя, которому нужны сами предки (сходство). */
export interface LineageWalkRow {
  rootId: string;
  kind: "philosopher" | "concept";
  /** Ключ предка: имя философа; у концепции — `id:<uuid>` (строка БД либо
   *  узел файла с вписанным идентификатором) или `file:<имя>` (снимок
   *  файла без идентификатора; имя приведено — регистр, пробелы, кавычки) */
  key: string;
  /** Имя для показа: философ, название концепции из БД, имя узла файла */
  label: string;
  /** id концепции-предка со строкой в БД; null — снимок файла / философ */
  synthesisId: string | null;
  depth: number;
}

/**
 * Имя узла-концепции файла для сравнения — SQL-вид `normalizeConceptTitle`
 * (8.5): снять кавычки, схлопнуть пробелы, нижний регистр. Имя — не
 * идентификатор: по нему сходятся только снимки файла между собой, со
 * строками БД снимок сравнивается лишь по вписанному в файл идентификатору.
 */
const FILE_NAME_KEY = sql`lower(btrim(regexp_replace(regexp_replace(coalesce(w.name, ''), '[«»"„“”‟'']', '', 'g'), '[[:space:]]+', ' ', 'g')))`;
const UUID_SQL_RE = "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$";

/**
 * Предки названных концепций — строками (корень сам в ответ не входит).
 * Безымянные узлы файла (14.2: `unnamed`, пустое имя, прежние русские
 * заглушки) пропускаются: сравнивать их не с чем.
 */
export async function loadLineageWalk(rootIds: readonly string[]): Promise<LineageWalkRow[]> {
  const ids = [...new Set(rootIds)];
  if (ids.length === 0) return [];
  const rows = await sql<
    { root_id: string; kind: "philosopher" | "concept"; key: string; label: string | null; sid: string | null; depth: number }[]
  >`
    WITH RECURSIVE ${lineageWalkCte(sql`s.id IN ${sql(ids)}`)}
    SELECT DISTINCT ON (w.root_id, w.kind, key) w.root_id, w.kind, w.sid, w.depth,
           CASE WHEN w.kind = 'philosopher' THEN w.name
                WHEN w.sid IS NOT NULL THEN 'id:' || w.sid::text
                WHEN coalesce(w.node ->> 'synthesisId', '') ~ ${UUID_SQL_RE} THEN 'id:' || lower(w.node ->> 'synthesisId')
                ELSE 'file:' || ${FILE_NAME_KEY} END AS key,
           CASE WHEN w.sid IS NOT NULL THEN t.title ELSE w.name END AS label
    FROM walk w
    LEFT JOIN syntheses t ON t.id = w.sid
    WHERE w.depth > 0
      AND (w.sid IS NOT NULL
           OR (coalesce(btrim(w.name), '') NOT IN ('', '[безымянная концепция]', '[безымянный философ]')
               AND coalesce(w.node ->> 'unnamed', 'false') <> 'true'))
    ORDER BY w.root_id, w.kind, key, w.depth`;
  return rows.map((r) => ({
    rootId: r.root_id,
    kind: r.kind,
    key: r.key,
    label: r.label ?? "",
    synthesisId: r.sid,
    depth: r.depth,
  }));
}
