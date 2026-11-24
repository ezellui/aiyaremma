package xdb.l10n;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.io.UnsupportedEncodingException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TimeZone;
import java.util.TreeMap;

import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import xdb.l10n.Model.NoteEntry;
import xdb.l10n.Model.NoteUnit;
import xdb.l10n.Model.Override;
import xdb.l10n.Model.Owner;
import xdb.l10n.Model.Page;
import xdb.l10n.Model.Use;
import xdb.l10n.Model.Uses;
import xdb.l10n.TaskFile.Item;

/**
 * Command line tools for the translation of the Eldamo data. See L10N-ru.md.
 *
 * <pre>
 * make   — create the skeleton of a translation base from the English base
 * task   — make a translation task: what is new, changed or untranslated
 * apply  — put a translated task into the translation base
 * check  — find untranslated and suspicious translations in a base or a task
 * sync   — accept the current English base as synchronized (without a task)
 * prune  — remove translations of things that are no longer in the English base
 * </pre>
 */
public final class L10n {

    private static final String DEFAULT_EN = "src/data/eldamo-data.xml";
    private static final String DEFAULT_MESSAGES = "src/main/webapp/config/messages/messages-%s.xml";
    private static final List<String> NOTE_GROUPS = Arrays.asList("lead", "main", "cd", "neo", "other");
    private static final List<String> OWNER_KINDS = Arrays.asList("word", "language", "source");

    private final Map<String, String> opts = new HashMap<String, String>();
    private final PrintStream out;

    private L10n(PrintStream out) {
        this.out = out;
    }

    public static void main(String[] args) throws Exception {
        PrintStream console = new PrintStream(new FileOutputStream(java.io.FileDescriptor.out), true, "UTF-8");
        if (args.length == 0 || args[0].equals("help") || args[0].equals("--help")) {
            usage(console);
            return;
        }
        L10n tool = new L10n(console);
        for (int i = 1; i < args.length; i++) {
            String a = args[i];
            if (!a.startsWith("--")) {
                throw new IllegalArgumentException("Unexpected argument: " + a);
            }
            String key = a.substring(2);
            int eq = key.indexOf('=');
            if (eq >= 0) {
                tool.opts.put(key.substring(0, eq), key.substring(eq + 1));
            } else if (i + 1 < args.length && !args[i + 1].startsWith("--")) {
                tool.opts.put(key, args[++i]);
            } else {
                tool.opts.put(key, "true");
            }
        }
        int status;
        try {
            status = tool.run(args[0]);
        } catch (IllegalArgumentException | IOException ex) {
            console.println("Ошибка: " + ex.getMessage());
            status = 2;
        }
        console.flush();
        if (status != 0) {
            System.exit(status);
        }
    }

    private static void usage(PrintStream o) {
        o.println("Инструменты перевода Eldamo (подробно: L10N-ru.md)");
        o.println();
        o.println("  make  [--en F] [--base F] [--lang ru] [--seed F|none] [--force]");
        o.println("        создать заготовку русской базы");
        o.println("  task  [--en F] [--base F] --out F [--scope delta|all] [--kinds gloss,title,phrase,label,notes]");
        o.println("        [--notes lead,main,cd,neo,other] [--owners word,language,source] [--langs q,s,...] [--limit N]");
        o.println("        сделать задание на перевод");
        o.println("  apply --task F [--base F] [--dry-run]");
        o.println("        внести переведённое задание в русскую базу");
        o.println("  check [--base F] [--en F|none] [--task F] [--list N] [--report F] [--fail]");
        o.println("        найти непереведённое и подозрительное");
        o.println("  sync  [--en F] [--base F]");
        o.println("        считать текущую английскую базу синхронизированной");
        o.println("  prune [--en F] [--base F] [--dry-run]");
        o.println("        удалить переводы того, чего больше нет в английской базе");
        o.println();
        o.println("По умолчанию --en " + DEFAULT_EN + ", --base src/data/eldamo-data-LANG.xml, --lang ru.");
    }

    private int run(String command) throws IOException {
        switch (command) {
            case "make": return make();
            case "task": return task();
            case "apply": return apply();
            case "check": return check();
            case "sync": return sync();
            case "prune": return prune();
            default:
                throw new IllegalArgumentException("Unknown command: " + command + " (see: help)");
        }
    }

    // ------------------------------------------------------------------ options

    private String lang() {
        return opt("lang", "ru");
    }

    private String opt(String name, String def) {
        String v = opts.get(name);
        return v == null ? def : v;
    }

    private File enFile() {
        return new File(opt("en", DEFAULT_EN));
    }

    private File baseFile() {
        return new File(opt("base", "src/data/eldamo-data-" + lang() + ".xml"));
    }

    private boolean flag(String name) {
        return "true".equals(opts.get(name));
    }

    private static Set<String> list(String value, List<String> allowed, String what) {
        Set<String> result = new LinkedHashSetOrdered();
        for (String s : value.split(",")) {
            s = s.trim();
            if (s.isEmpty()) {
                continue;
            }
            if (allowed != null && !allowed.contains(s)) {
                throw new IllegalArgumentException("Unknown " + what + ": " + s + " (allowed: " + allowed + ")");
            }
            result.add(s);
        }
        return result;
    }

    /** An insertion-ordered set (named to keep the imports short). */
    private static final class LinkedHashSetOrdered extends java.util.LinkedHashSet<String> {
        private static final long serialVersionUID = 1L;
    }

    private EnglishBase readEnglish() throws IOException {
        File f = enFile();
        if (!f.isFile()) {
            throw new IOException("English base not found: " + f);
        }
        long t = System.currentTimeMillis();
        EnglishBase en = EnglishBase.read(f);
        out.println("Английская база: " + f + " (версия " + en.version + ", " + en.pages.size() + " страниц, "
            + (System.currentTimeMillis() - t) + " мс)");
        return en;
    }

    private RuBase readBase() throws IOException {
        File f = baseFile();
        if (!f.isFile()) {
            throw new IOException("Translation base not found: " + f + " (create it with: make)");
        }
        RuBase base = RuBase.read(f);
        out.println("Русская база: " + f);
        return base;
    }

    private static String now() {
        SimpleDateFormat f = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'");
        f.setTimeZone(TimeZone.getTimeZone("UTC"));
        return f.format(new Date());
    }

    // ------------------------------------------------------------------ make

    private int make() throws IOException {
        File baseFile = baseFile();
        if (baseFile.exists() && !flag("force")) {
            throw new IOException(baseFile + " already exists (use --force to overwrite it)");
        }
        EnglishBase en = readEnglish();
        RuBase base = new RuBase();
        base.lang = lang();
        for (String table : Model.TABLES) {
            TreeMap<String, String> t = base.tables.get(table);
            for (String s : en.tables.get(table).keySet()) {
                t.put(s, "");
            }
        }
        String seed = opt("seed", String.format(DEFAULT_MESSAGES, lang()));
        if (!seed.equals("none")) {
            File seedFile = new File(seed);
            if (seedFile.isFile()) {
                int n = seedLabels(en, base, seedFile);
                out.println("Из каталога интерфейса " + seedFile + " взято названий языков: " + n);
            } else if (opts.containsKey("seed")) {
                throw new IOException("Seed catalog not found: " + seedFile);
            }
        }
        base.takeSnapshot(en);
        base.synced = now();
        base.write(baseFile);
        out.println("Создана заготовка: " + baseFile);
        stats(en, base, out);
        return 0;
    }

    /** Language and language-category names from the interface catalog, into the label table. */
    private static int seedLabels(EnglishBase en, RuBase base, File catalog) throws IOException {
        Map<String, String> catIds = new HashMap<String, String>();
        for (Map.Entry<String, Uses> e : en.tables.get("label").entrySet()) {
            for (Use u : e.getValue().sample) {
                if (u.ctx.startsWith("language-cat:")) {
                    catIds.put(u.ctx.substring("language-cat:".length()), e.getKey());
                }
            }
        }
        TreeMap<String, String> labels = base.tables.get("label");
        int n = 0;
        try (InputStream in = XmlIO.open(catalog)) {
            XMLStreamReader r = XmlIO.reader(in);
            while (r.hasNext()) {
                if (r.next() != XMLStreamConstants.START_ELEMENT) {
                    continue;
                }
                String name = r.getLocalName();
                Map<String, String> a = XmlIO.attributes(r);
                String english = null;
                if (name.equals("language")) {
                    Owner o = en.owners.get("language|" + a.get("id"));
                    english = o == null ? null : o.name;
                } else if (name.equals("language-cat")) {
                    english = a.containsKey("id") ? catIds.get(a.get("id")) : a.get("name");
                } else {
                    continue;
                }
                String text = XmlIO.text(r).trim();
                if (english != null && !text.isEmpty() && labels.containsKey(english)
                    && labels.get(english).isEmpty()) {
                    labels.put(english, text);
                    n++;
                }
            }
        } catch (XMLStreamException ex) {
            throw new IOException("Cannot read " + catalog + ": " + ex.getMessage(), ex);
        }
        return n;
    }

    // ------------------------------------------------------------------ task

    private int task() throws IOException {
        String outName = opts.get("out");
        if (outName == null) {
            throw new IllegalArgumentException("--out is required");
        }
        String scope = opt("scope", "delta");
        if (!scope.equals("delta") && !scope.equals("all")) {
            throw new IllegalArgumentException("--scope must be delta or all");
        }
        List<String> allKinds = new ArrayList<String>(Model.TABLES);
        allKinds.add("notes");
        String defaultKinds = scope.equals("all") ? "gloss,title,phrase,label" : "gloss,title,phrase,label,notes";
        Set<String> kinds = list(opt("kinds", defaultKinds), allKinds, "kind");
        Set<String> groups = list(opt("notes", "lead,main,cd,neo,other"), NOTE_GROUPS, "notes group");
        Set<String> ownerKinds = list(opt("owners", "word,language,source"), OWNER_KINDS, "owner kind");
        Set<String> langs = opts.containsKey("langs") ? list(opts.get("langs"), null, "language") : null;
        int limit = Integer.parseInt(opt("limit", "0"));

        EnglishBase en = readEnglish();
        RuBase base = readBase();
        checkLang(base);
        TaskFile task = new TaskFile();
        task.lang = base.lang;
        task.baseVersion = en.version;
        task.fromSnapshot = base.snapshotId;
        task.toSnapshot = en.snapshotId();
        task.created = now();
        task.scope = scope;
        List<String> filters = new ArrayList<String>();
        for (String key : Arrays.asList("kinds", "notes", "owners", "langs", "limit")) {
            if (opts.containsKey(key)) {
                filters.add(key + "=" + opts.get(key));
            }
        }
        task.filters = filters.isEmpty() ? null : String.join(" ", filters);

        // the delta of pages and owners since the snapshot
        Map<String, List<String[]>> glossHints = new HashMap<String, List<String[]>>();
        for (Page p : en.pages.values()) {
            Page old = base.pages.get(p.id);
            if (old == null) {
                task.added.add(p);
            } else {
                List<String> diff = p.diff(old);
                if (!diff.isEmpty()) {
                    task.changed.add(p);
                    task.changes.put(p.id, diff);
                    for (String field : Arrays.asList("gloss", "ngloss")) {
                        String a = old.field(field);
                        String b = p.field(field);
                        if (a != null && b != null && !a.equals(b)) {
                            String ru = translation(base, p.id, field, a);
                            if (ru != null) {
                                List<String[]> hints = glossHints.get(b.trim());
                                if (hints == null) {
                                    hints = new ArrayList<String[]>();
                                    glossHints.put(b.trim(), hints);
                                }
                                hints.add(new String[] {p.id, a, ru});
                            }
                        }
                    }
                }
            }
        }
        for (Page old : base.pages.values()) {
            if (!en.pages.containsKey(old.id)) {
                task.removed.add(old);
            }
        }
        for (Owner o : en.owners.values()) {
            Owner old = base.owners.get(o.key());
            if (old == null || !Objects.equals(old.name, o.name) || !old.segs.equals(o.segs)) {
                task.ownersChanged.add(o);
            }
        }
        for (Owner old : base.owners.values()) {
            if (!en.owners.containsKey(old.key())) {
                task.ownersRemoved.add(old);
            }
        }

        // items: changed first, then new, then untranslated
        List<Item> changedItems = new ArrayList<Item>();
        List<Item> newItems = new ArrayList<Item>();
        List<Item> untranslated = new ArrayList<Item>();
        for (String table : Model.TABLES) {
            if (!kinds.contains(table)) {
                continue;
            }
            TreeMap<String, String> translations = base.tables.get(table);
            for (Map.Entry<String, Uses> e : en.tables.get(table).entrySet()) {
                Uses uses = e.getValue();
                if (langs != null && !uses.langs.isEmpty() && !intersects(langs, uses.langs)) {
                    continue;
                }
                String ru = translations.get(e.getKey());
                boolean missing = ru == null;
                if (!missing && (!ru.isEmpty() || scope.equals("delta"))) {
                    continue;
                }
                Item item = new Item();
                item.kind = table;
                item.status = missing ? "new" : "untranslated";
                item.en = e.getKey();
                item.uses.addAll(uses.sample);
                if (uses.count > uses.sample.size()) {
                    item.context = "всего употреблений: " + uses.count;
                }
                List<String[]> hints = glossHints.get(e.getKey());
                if (hints != null && table.equals("gloss")) {
                    item.hints.addAll(hints);
                }
                (missing ? newItems : untranslated).add(item);
            }
        }
        if (kinds.contains("gloss")) {
            for (Override o : base.overrides.values()) {
                Page p = en.pages.get(o.pageId);
                if (p == null) {
                    continue;
                }
                String current = p.field(o.field);
                if (current != null && !current.trim().equals(o.en)) {
                    if (langs != null && !langs.contains(p.l)) {
                        continue;
                    }
                    Item item = new Item();
                    item.kind = "gloss-override";
                    item.status = "changed";
                    item.pageId = o.pageId;
                    item.field = o.field;
                    item.en = current.trim();
                    item.oldEn = o.en;
                    item.oldRu = o.ru;
                    item.ru = "";
                    item.context = p.l + " " + p.v;
                    changedItems.add(item);
                }
            }
        }
        if (kinds.contains("notes")) {
            for (NoteUnit u : en.notes.values()) {
                if (!ownerKinds.contains(u.owner) || !groups.contains(Notes.group(u.seg))) {
                    continue;
                }
                if (langs != null && (u.l == null || !langs.contains(u.l))) {
                    continue;
                }
                NoteEntry entry = base.notes.get(u.key());
                boolean translated = entry != null && entry.ru != null && !entry.ru.trim().isEmpty();
                Item item = noteItem(u, en);
                if (translated) {
                    if (entry.hash.equals(u.hash)) {
                        continue;
                    }
                    item.status = "changed";
                    item.oldEn = entry.en;
                    item.oldRu = entry.ru;
                    item.ru = entry.ru;
                    changedItems.add(item);
                } else {
                    String oldHash = snapshotHash(base, u);
                    boolean fresh = oldHash == null || !oldHash.equals(u.hash);
                    if (fresh) {
                        item.status = oldHash == null ? "new" : "changed-untranslated";
                        newItems.add(item);
                    } else if (scope.equals("all")) {
                        item.status = "untranslated";
                        untranslated.add(item);
                    }
                }
            }
        }
        task.items.addAll(changedItems);
        task.items.addAll(newItems);
        task.items.addAll(untranslated);
        int total = task.items.size();
        if (limit > 0 && task.items.size() > limit) {
            task.items.subList(limit, task.items.size()).clear();
        }
        task.complete = filters.isEmpty() && scope.equals("delta");

        // orphans: translations of things that are gone
        for (String table : Model.TABLES) {
            for (Map.Entry<String, String> e : base.tables.get(table).entrySet()) {
                if (!e.getValue().isEmpty() && !en.tables.get(table).containsKey(e.getKey())) {
                    Item item = new Item();
                    item.kind = table;
                    item.status = "orphan";
                    item.en = e.getKey();
                    item.oldRu = e.getValue();
                    task.orphans.add(item);
                }
            }
        }
        for (Override o : base.overrides.values()) {
            if (!en.pages.containsKey(o.pageId)) {
                Item item = new Item();
                item.kind = "gloss-override";
                item.status = "orphan";
                item.pageId = o.pageId;
                item.field = o.field;
                item.en = o.en;
                item.oldRu = o.ru;
                task.orphans.add(item);
            }
        }
        for (NoteEntry n : base.notes.values()) {
            if (!en.notes.containsKey(n.key())) {
                Item item = new Item();
                item.kind = "notes";
                item.status = "orphan";
                item.owner = n.owner;
                item.id = n.id;
                item.part = n.part;
                item.seg = n.seg;
                item.hash = n.hash;
                item.en = n.en;
                item.oldRu = n.ru;
                task.orphans.add(item);
            }
        }

        Map<String, Integer> byKind = new TreeMap<String, Integer>();
        Map<String, Integer> byStatus = new TreeMap<String, Integer>();
        for (Item i : task.items) {
            increment(byKind, i.kind);
            increment(byStatus, i.status);
        }
        StringBuilder summary = new StringBuilder();
        summary.append("Страниц добавлено: ").append(task.added.size()).append(", удалено: ")
            .append(task.removed.size()).append(", изменено: ").append(task.changed.size())
            .append(". Языков/источников изменено: ").append(task.ownersChanged.size())
            .append(", удалено: ").append(task.ownersRemoved.size()).append(". Единиц к переводу: ")
            .append(task.items.size());
        if (task.items.size() < total) {
            summary.append(" (из ").append(total).append(", ограничено --limit)");
        }
        summary.append(" ").append(byKind).append(" ").append(byStatus).append(". Устаревших переводов: ")
            .append(task.orphans.size()).append(".");
        task.summary = summary.toString();
        File outFile = new File(outName);
        task.write(outFile);
        out.println(task.summary);
        out.println("Задание записано: " + outFile);
        if (!task.complete) {
            out.println("Задание неполное (фильтры или --scope all): после внесения снимок английской базы "
                + "не обновится; используйте полное задание или команду sync.");
        }
        return 0;
    }

    private static Item noteItem(NoteUnit u, EnglishBase en) {
        Item item = new Item();
        item.kind = "notes";
        item.owner = u.owner;
        item.id = u.id;
        item.part = u.part;
        item.seg = u.seg;
        item.hash = u.hash;
        item.en = u.text;
        StringBuilder ctx = new StringBuilder();
        if (u.owner.equals("word")) {
            Page p = en.pages.get(u.id);
            ctx.append(p.l).append(" ").append(p.v);
            if (p.gloss != null) {
                ctx.append(" “").append(p.gloss).append("”");
            }
        } else {
            ctx.append(u.label == null ? u.id : u.label);
        }
        item.context = ctx.toString();
        return item;
    }

    private static String snapshotHash(RuBase base, NoteUnit u) {
        Map<String, String> segs = null;
        if (u.owner.equals("word")) {
            Page p = base.pages.get(u.id);
            segs = p == null ? null : p.segs;
        } else {
            Owner o = base.owners.get(u.owner + "|" + u.id);
            segs = o == null ? null : o.segs;
        }
        return segs == null ? null : segs.get(u.part + "|" + u.seg);
    }

    /** The translation shown for a gloss of a page: the override or the table entry. */
    private static String translation(RuBase base, String pageId, String field, String en) {
        Override o = base.overrides.get(pageId + "|" + field);
        if (o != null && o.ru != null && !o.ru.isEmpty() && Objects.equals(o.en, en.trim())) {
            return o.ru;
        }
        String ru = base.tables.get("gloss").get(en.trim());
        return ru == null || ru.isEmpty() ? null : ru;
    }

    private static boolean intersects(Set<String> a, Set<String> b) {
        for (String s : b) {
            if (a.contains(s)) {
                return true;
            }
        }
        return false;
    }

    private static void increment(Map<String, Integer> map, String key) {
        Integer n = map.get(key);
        map.put(key, n == null ? 1 : n + 1);
    }

    private void checkLang(RuBase base) {
        if (opts.containsKey("lang") && !lang().equals(base.lang)) {
            throw new IllegalArgumentException("The base is for language " + base.lang + ", not " + lang());
        }
    }

    // ------------------------------------------------------------------ apply

    private int apply() throws IOException {
        String taskName = opts.get("task");
        if (taskName == null) {
            throw new IllegalArgumentException("--task is required");
        }
        TaskFile task = TaskFile.read(new File(taskName));
        RuBase base = readBase();
        if (task.lang != null && !task.lang.equals(base.lang)) {
            throw new IllegalArgumentException("The task is for language " + task.lang + ", the base for "
                + base.lang);
        }
        Map<String, Page> knownPages = new HashMap<String, Page>(base.pages);
        for (Page p : task.added) {
            knownPages.put(p.id, p);
        }
        for (Page p : task.changed) {
            knownPages.put(p.id, p);
        }
        Map<String, Integer> counts = new LinkedHashMap<String, Integer>();
        int problems = 0;
        for (Item i : task.items) {
            String ru = i.ru == null ? "" : i.ru.trim();
            if (i.isNotes()) {
                if (ru.isEmpty()) {
                    increment(counts, "заметки: не переведено");
                    continue;
                }
                NoteEntry n = new NoteEntry();
                n.owner = i.owner;
                n.id = i.id;
                n.part = i.part;
                n.seg = i.seg;
                n.hash = i.hash;
                n.en = i.en;
                n.ru = i.ru.trim();
                base.notes.put(n.key(), n);
                increment(counts, "заметки: внесено");
            } else if (i.kind.equals("gloss-override")) {
                String key = i.pageId + "|" + i.field;
                if (ru.isEmpty()) {
                    if (base.overrides.remove(key) != null) {
                        increment(counts, "индивидуальные глоссы: удалено");
                    }
                } else {
                    putOverride(base, i.pageId, i.field, i.en, ru);
                    increment(counts, "индивидуальные глоссы: внесено");
                }
            } else {
                TreeMap<String, String> table = base.tables.get(i.kind);
                if (table == null) {
                    throw new IOException("Unknown item kind in the task: " + i.kind);
                }
                String old = table.get(i.en);
                if (!ru.isEmpty()) {
                    table.put(i.en, ru);
                    increment(counts, i.kind + ": внесено");
                } else if (old == null) {
                    table.put(i.en, "");
                    increment(counts, i.kind + ": зарегистрировано без перевода");
                } else {
                    increment(counts, i.kind + ": не переведено");
                }
                for (Map.Entry<String, String> o : i.overrides.entrySet()) {
                    Page p = knownPages.get(o.getKey());
                    String field = p != null && p.ngloss != null && p.ngloss.trim().equals(i.en)
                        && (p.gloss == null || !p.gloss.trim().equals(i.en)) ? "ngloss" : "gloss";
                    if (o.getValue().isEmpty()) {
                        base.overrides.remove(o.getKey() + "|" + field);
                    } else {
                        putOverride(base, o.getKey(), field, i.en, o.getValue());
                        increment(counts, "индивидуальные глоссы: внесено");
                    }
                }
            }
            if (!ru.isEmpty() && !Checks.check(i.en, ru, i.isNotes()).isEmpty()) {
                problems++;
            }
        }
        boolean advance = task.complete && task.toSnapshot != null
            && Objects.equals(task.fromSnapshot, base.snapshotId);
        if (advance) {
            for (Page p : task.removed) {
                base.pages.remove(p.id);
            }
            for (Page p : task.added) {
                base.pages.put(p.id, p);
            }
            for (Page p : task.changed) {
                base.pages.put(p.id, p);
            }
            for (Owner o : task.ownersRemoved) {
                base.owners.remove(o.key());
            }
            for (Owner o : task.ownersChanged) {
                base.owners.put(o.key(), o);
            }
            base.snapshotId = task.toSnapshot;
            base.baseVersion = task.baseVersion;
            base.synced = now();
        }
        for (Map.Entry<String, Integer> c : counts.entrySet()) {
            out.println("  " + c.getKey() + ": " + c.getValue());
        }
        if (advance) {
            out.println("Снимок английской базы обновлён до " + task.toSnapshot + " (версия " + task.baseVersion + ").");
        } else if (!task.complete) {
            out.println("Задание неполное: снимок английской базы не обновлён (при необходимости: sync).");
        } else {
            out.println("Снимок английской базы не обновлён: задание сделано не от текущего состояния русской базы "
                + "(" + task.fromSnapshot + " ≠ " + base.snapshotId + ").");
        }
        if (problems > 0) {
            out.println("Подозрительных переводов: " + problems + " (подробно: check --task " + taskName + ")");
        }
        if (flag("dry-run")) {
            out.println("Пробный запуск: русская база не изменена.");
        } else {
            base.write(baseFile());
            out.println("Русская база записана: " + baseFile());
        }
        return 0;
    }

    private static void putOverride(RuBase base, String pageId, String field, String en, String ru) {
        Override o = new Override();
        o.pageId = pageId;
        o.field = field;
        o.en = en;
        o.ru = ru;
        base.overrides.put(o.key(), o);
    }

    // ------------------------------------------------------------------ check

    /** Found problems: code -> descriptions. */
    private static final class Report {
        final Map<String, List<String>> problems = new LinkedHashMap<String, List<String>>();

        Report() {
            for (String code : Checks.CODES) {
                problems.put(code, new ArrayList<String>());
            }
        }

        void add(String code, String text) {
            problems.get(code).add(text);
        }

        int total() {
            int n = 0;
            for (List<String> l : problems.values()) {
                n += l.size();
            }
            return n;
        }

        void print(PrintStream o, int max) {
            for (Map.Entry<String, List<String>> e : problems.entrySet()) {
                if (e.getValue().isEmpty()) {
                    continue;
                }
                o.println();
                o.println("[" + e.getKey() + "] " + Checks.describe(e.getKey()) + ": " + e.getValue().size());
                int n = 0;
                for (String s : e.getValue()) {
                    if (max >= 0 && n++ >= max) {
                        o.println("    … ещё " + (e.getValue().size() - max));
                        break;
                    }
                    o.println("    " + s);
                }
            }
        }
    }

    private int check() throws IOException {
        int max = Integer.parseInt(opt("list", "20"));
        PrintStream report = out;
        if (opts.containsKey("report")) {
            report = new PrintStream(new FileOutputStream(opts.get("report")), true, "UTF-8");
        }
        Report r = new Report();
        try {
            if (opts.containsKey("task")) {
                checkTask(TaskFile.read(new File(opts.get("task"))), r, report);
            } else {
                RuBase base = readBase();
                EnglishBase en = opt("en", "").equals("none") ? null : readEnglish();
                checkBase(base, en, r, report);
            }
            r.print(report, max);
            report.println();
            report.println("Всего замечаний: " + r.total());
        } finally {
            if (report != out) {
                report.close();
                out.println("Отчёт записан: " + opts.get("report") + " (замечаний: " + r.total() + ")");
            }
        }
        return flag("fail") && r.total() > 0 ? 1 : 0;
    }

    private static String shorten(String s) {
        String t = s.replaceAll("\\s+", " ").trim();
        return t.length() > 160 ? t.substring(0, 157) + "…" : t;
    }

    private static void checkTask(TaskFile task, Report r, PrintStream o) {
        o.println("Задание: " + task.items.size() + " единиц, scope=" + task.scope
            + (task.filters == null ? "" : ", " + task.filters));
        int done = 0;
        for (Item i : task.items) {
            String ru = i.ru == null ? "" : i.ru;
            List<String> problems = new ArrayList<String>(Checks.check(i.en, ru, i.isNotes()));
            if (i.oldRu != null && !ru.trim().isEmpty() && ru.trim().equals(i.oldRu.trim())
                && i.oldEn != null && !i.oldEn.trim().equals(i.en == null ? "" : i.en.trim())) {
                problems.add("not-updated");
            }
            if (!problems.contains("empty")) {
                done++;
            }
            for (String p : problems) {
                r.add(p, i.label() + (ru.trim().isEmpty() ? "" : " → " + shorten(ru)));
            }
        }
        o.println("Переведено: " + done + " из " + task.items.size());
    }

    private static void checkBase(RuBase base, EnglishBase en, Report r, PrintStream o) {
        for (Map.Entry<String, TreeMap<String, String>> t : base.tables.entrySet()) {
            for (Map.Entry<String, String> e : t.getValue().entrySet()) {
                if (en != null && !en.tables.get(t.getKey()).containsKey(e.getKey())) {
                    if (!e.getValue().isEmpty()) {
                        r.add("orphan", t.getKey() + ": " + e.getKey());
                    }
                    continue;
                }
                for (String p : Checks.check(e.getKey(), e.getValue(), false)) {
                    r.add(p, t.getKey() + ": " + e.getKey() + (e.getValue().isEmpty() ? "" : " → "
                        + shorten(e.getValue())));
                }
            }
            if (en != null) {
                for (String s : en.tables.get(t.getKey()).keySet()) {
                    if (!t.getValue().containsKey(s)) {
                        r.add("missing", t.getKey() + ": " + s);
                    }
                }
            }
        }
        for (Override ov : base.overrides.values()) {
            String label = "gloss " + ov.field + " of page " + ov.pageId + ": " + ov.en;
            if (en != null) {
                Page p = en.pages.get(ov.pageId);
                if (p == null) {
                    r.add("orphan", label);
                    continue;
                }
                String current = p.field(ov.field);
                if (current == null || !current.trim().equals(ov.en)) {
                    r.add("stale", label + " (сейчас: " + current + ")");
                }
            }
            for (String p : Checks.check(ov.en, ov.ru, false)) {
                r.add(p, label + " → " + shorten(ov.ru == null ? "" : ov.ru));
            }
        }
        for (NoteEntry n : base.notes.values()) {
            String label = "notes " + n.owner + " " + n.id + " " + n.part + "/" + n.seg;
            if (en != null) {
                NoteUnit u = en.notes.get(n.key());
                if (u == null) {
                    r.add("orphan", label);
                    continue;
                }
                if (!u.hash.equals(n.hash)) {
                    r.add("stale", label);
                }
            }
            for (String p : Checks.check(n.en, n.ru, true)) {
                r.add(p, label);
            }
        }
        if (en != null) {
            stats(en, base, o);
        }
    }

    /** Coverage of the translation. */
    private static void stats(EnglishBase en, RuBase base, PrintStream o) {
        o.println("Покрытие перевода:");
        for (String table : Model.TABLES) {
            int total = 0;
            int done = 0;
            long uses = 0;
            long usesDone = 0;
            for (Map.Entry<String, Uses> e : en.tables.get(table).entrySet()) {
                total++;
                uses += e.getValue().count;
                String ru = base.tables.get(table).get(e.getKey());
                if (ru != null && !ru.isEmpty()) {
                    done++;
                    usesDone += e.getValue().count;
                }
            }
            o.println(String.format("  %-7s %6d из %6d строк (%s), %7d из %7d употреблений (%s)", table, done, total,
                pct(done, total), usesDone, uses, pct(usesDone, uses)));
        }
        Map<String, int[]> notes = new TreeMap<String, int[]>();
        for (NoteUnit u : en.notes.values()) {
            String group = u.owner + "/" + Notes.group(u.seg);
            int[] c = notes.get(group);
            if (c == null) {
                c = new int[3];
                notes.put(group, c);
            }
            c[0]++;
            NoteEntry n = base.notes.get(u.key());
            if (n != null && n.ru != null && !n.ru.trim().isEmpty()) {
                if (n.hash.equals(u.hash)) {
                    c[1]++;
                } else {
                    c[2]++;
                }
            }
        }
        for (Map.Entry<String, int[]> e : notes.entrySet()) {
            int[] c = e.getValue();
            o.println(String.format("  заметки %-15s %6d из %6d (%s)%s", e.getKey(), c[1], c[0], pct(c[1], c[0]),
                c[2] > 0 ? ", устарело: " + c[2] : ""));
        }
        o.println("  индивидуальных глоссов: " + base.overrides.size());
    }

    private static String pct(long a, long b) {
        return b == 0 ? "—" : String.format("%.1f%%", 100.0 * a / b);
    }

    // ------------------------------------------------------------------ sync, prune

    private int sync() throws IOException {
        EnglishBase en = readEnglish();
        RuBase base = readBase();
        checkLang(base);
        String old = base.snapshotId;
        base.takeSnapshot(en);
        base.synced = now();
        base.write(baseFile());
        out.println("Снимок английской базы: " + old + " → " + base.snapshotId + " (версия " + base.baseVersion + ").");
        out.println("Внимание: новые и изменённые заметки без перевода больше не попадут в задание --scope delta;"
            + " их покажут --scope all и check.");
        return 0;
    }

    private int prune() throws IOException {
        EnglishBase en = readEnglish();
        RuBase base = readBase();
        checkLang(base);
        int n = 0;
        for (String table : Model.TABLES) {
            Set<String> keep = en.tables.get(table).keySet();
            for (java.util.Iterator<String> it = base.tables.get(table).keySet().iterator(); it.hasNext();) {
                if (!keep.contains(it.next())) {
                    it.remove();
                    n++;
                }
            }
        }
        for (java.util.Iterator<Override> it = base.overrides.values().iterator(); it.hasNext();) {
            if (!en.pages.containsKey(it.next().pageId)) {
                it.remove();
                n++;
            }
        }
        for (java.util.Iterator<NoteEntry> it = base.notes.values().iterator(); it.hasNext();) {
            if (!en.notes.containsKey(it.next().key())) {
                it.remove();
                n++;
            }
        }
        out.println("Удалено устаревших записей: " + n);
        if (flag("dry-run")) {
            out.println("Пробный запуск: русская база не изменена.");
        } else {
            base.write(baseFile());
        }
        return 0;
    }

    static {
        // keep javac quiet about the unused import on some compilers
        Objects.requireNonNull(HashSet.class);
    }

    @SuppressWarnings("unused")
    private static void unused() throws UnsupportedEncodingException {
    }
}
