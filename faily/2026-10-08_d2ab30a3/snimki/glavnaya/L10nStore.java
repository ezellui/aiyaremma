package xdb.l10n;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;

import xdb.l10n.Model.NoteEntry;
import xdb.l10n.Model.Override;

/**
 * Translations of the data shown on the site: the translation base of a language
 * (DATA_ROOT/eldamo-data-LANG.xml), loaded on first use and reloaded when the file changes.
 *
 * <p>
 * A missing or unreadable base simply leaves everything untranslated.
 * </p>
 */
public final class L10nStore {
    private static final Logger LOGGER = Logger.getLogger(L10nStore.class.getName());
    private static final long CHECK_INTERVAL_MS = 2000;
    private static final Map<String, Holder> HOLDERS = new ConcurrentHashMap<String, Holder>();
    private static volatile String dataRoot;

    private L10nStore() {
    }

    /** The directory of the translation bases; by default the data root of the site. */
    public static void setDataRoot(String root) {
        dataRoot = root;
        HOLDERS.clear();
    }

    private static String dataRoot() {
        String root = dataRoot;
        return root != null ? root : xdb.dom.DomManager.getDataRoot();
    }

    /** Translations of one language, as used at run time. */
    static final class Data {
        static final Data EMPTY = new Data();
        final Map<String, Map<String, String>> tables = new HashMap<String, Map<String, String>>();
        final Map<String, Override> overrides = new HashMap<String, Override>();
        final Map<String, NoteEntry> notes = new HashMap<String, NoteEntry>();

        static Data of(RuBase base) {
            Data data = new Data();
            for (Map.Entry<String, java.util.TreeMap<String, String>> t : base.tables.entrySet()) {
                Map<String, String> table = new HashMap<String, String>();
                for (Map.Entry<String, String> e : t.getValue().entrySet()) {
                    if (e.getValue() != null && !e.getValue().isEmpty()) {
                        table.put(e.getKey(), e.getValue());
                    }
                }
                data.tables.put(t.getKey(), table);
            }
            for (Override o : base.overrides.values()) {
                if (o.ru != null && !o.ru.isEmpty()) {
                    data.overrides.put(o.key(), o);
                }
            }
            for (NoteEntry n : base.notes.values()) {
                if (n.ru != null && !n.ru.trim().isEmpty()) {
                    data.notes.put(n.key(), n);
                }
            }
            return data;
        }
    }

    private static final class Holder {
        final File file;
        volatile Data data = Data.EMPTY;
        volatile long modified = -1;
        volatile long checked;

        Holder(File file) {
            this.file = file;
        }

        Data get() {
            long now = System.currentTimeMillis();
            if (now - checked > CHECK_INTERVAL_MS) {
                synchronized (this) {
                    if (now - checked > CHECK_INTERVAL_MS) {
                        long m = file.isFile() ? file.lastModified() : 0;
                        if (m != modified) {
                            data = load();
                            modified = m;
                        }
                        checked = System.currentTimeMillis();
                    }
                }
            }
            return data;
        }

        private Data load() {
            if (!file.isFile()) {
                return Data.EMPTY;
            }
            try {
                long t = System.currentTimeMillis();
                Data d = Data.of(RuBase.read(file));
                LOGGER.info("Loaded " + file + " in " + (System.currentTimeMillis() - t) + " ms");
                return d;
            } catch (IOException | RuntimeException ex) {
                LOGGER.log(Level.WARNING, "Cannot load " + file, ex);
                return Data.EMPTY;
            }
        }
    }

    static Data data(String lang) {
        if (lang == null || !lang.matches("[a-z]{2,3}") || lang.equals("en")) {
            return Data.EMPTY;
        }
        String root = dataRoot();
        if (root == null) {
            return Data.EMPTY;
        }
        Holder holder = HOLDERS.get(lang);
        if (holder == null) {
            holder = new Holder(new File(root, "eldamo-data-" + lang + ".xml"));
            Holder existing = HOLDERS.putIfAbsent(lang, holder);
            if (existing != null) {
                holder = existing;
            }
        }
        return holder.get();
    }

    private static String resolve(String ru, String en) {
        return Checks.SAME_AS_ENGLISH.equals(ru) ? en : ru;
    }

    /**
     * Translation of a string of a table (gloss, title, phrase, label).
     *
     * @return The translation; empty if there is none.
     */
    public static String text(String table, String lang, String en) {
        if (en == null) {
            return "";
        }
        Map<String, String> t = data(lang).tables.get(table);
        String key = en.trim();
        String ru = t == null ? null : t.get(key);
        return ru == null ? "" : resolve(ru, key);
    }

    /**
     * Translation of the gloss (field "gloss") or neo-gloss ("ngloss") of a page: the translation
     * given for the page, if it was made for the current English gloss, or else the gloss table.
     *
     * @return The translation; empty if there is none.
     */
    public static String gloss(String lang, String field, String pageId, String en) {
        if (en == null) {
            return "";
        }
        String key = en.trim();
        Data d = data(lang);
        Override o = d.overrides.get(pageId + "|" + field);
        if (o != null && key.equals(o.en)) {
            return resolve(o.ru, key);
        }
        String ru = d.tables.get("gloss") == null ? null : d.tables.get("gloss").get(key);
        return ru == null ? "" : resolve(ru, key);
    }

    /**
     * Notes with every segment replaced by its translation, when the translation was made from
     * the current English text of the segment. Untranslated and outdated segments stay English.
     *
     * @return The notes.
     */
    public static String notes(String lang, String owner, String id, String part, String html) {
        if (html == null) {
            return "";
        }
        Data d = data(lang);
        if (d.notes.isEmpty()) {
            return html;
        }
        List<Notes.Segment> segments = Notes.split(html);
        StringBuilder sb = new StringBuilder(html.length() + 64);
        int pos = 0;
        for (Notes.Segment s : segments) {
            int start = html.indexOf(s.text, pos);
            if (start < 0) {
                return html; // cannot happen: segments are substrings in order
            }
            sb.append(html, pos, start);
            NoteEntry n = d.notes.get(Model.noteKey(owner, id, part, s.name));
            if (n != null && n.hash.equals(Notes.hash(s.text))) {
                String lead = s.text.substring(0, s.text.length() - s.text.replaceAll("^\\s+", "").length());
                String trail = s.text.substring(s.text.replaceAll("\\s+$", "").length());
                sb.append(lead).append(n.ru.trim()).append(trail);
            } else {
                sb.append(s.text);
            }
            pos = start + s.text.length();
        }
        sb.append(html, pos, html.length());
        return sb.toString();
    }
}
