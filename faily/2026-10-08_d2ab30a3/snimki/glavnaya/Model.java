package xdb.l10n;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Shared data classes of the translation tools. */
final class Model {

    private Model() {
    }

    /** Text-keyed tables of the Russian base. */
    static final List<String> TABLES = Collections.unmodifiableList(Arrays.asList("gloss", "title", "phrase", "label"));

    /** Parts of speech whose headword (@v) is an English title written by the editor. */
    static final Set<String> TITLE_SPEECH = Collections.unmodifiableSet(new HashSet<String>(
        Arrays.asList("grammar", "phonetic-rule", "phonetic-group", "text")));

    /** Elements whose text is editorial apparatus (the "phrase" table). */
    static final Set<String> PHRASE_ELEMENTS = Collections.unmodifiableSet(new HashSet<String>(
        Arrays.asList("related", "change", "correction", "deriv", "inflect", "element", "cognate", "before")));

    /** Prose sections of a language element. */
    static final Set<String> LANGUAGE_SECTIONS = Collections.unmodifiableSet(new HashSet<String>(
        Arrays.asList("notes", "words", "vocabulary", "neologisms", "deprecations", "grammar", "phonetics",
            "names", "phrases", "roots")));

    /** Key of a notes segment: owner kind, owner id, part (notes, notes#2, words...), segment. */
    static String noteKey(String owner, String id, String part, String seg) {
        return owner + "|" + id + "|" + part + "|" + seg;
    }

    /** Snapshot of a page (word) of the English base. */
    static final class Page {
        String id;
        String l;
        String v;
        String speech;
        String gloss;
        String ngloss;
        /** part|seg -> hash of the notes segments. */
        final Map<String, String> segs = new LinkedHashMap<String, String>();

        String title() {
            return speech != null && TITLE_SPEECH.contains(speech) ? v : null;
        }

        String field(String name) {
            if (name.equals("gloss")) {
                return gloss;
            } else if (name.equals("ngloss")) {
                return ngloss;
            }
            return null;
        }

        /** Differences to another snapshot of the same page, as "field: old -> new". */
        List<String> diff(Page old) {
            List<String> changes = new ArrayList<String>();
            add(changes, "l", old.l, l);
            add(changes, "v", old.v, v);
            add(changes, "speech", old.speech, speech);
            add(changes, "gloss", old.gloss, gloss);
            add(changes, "ngloss", old.ngloss, ngloss);
            if (!old.segs.equals(segs)) {
                Set<String> keys = new HashSet<String>(old.segs.keySet());
                keys.addAll(segs.keySet());
                for (String key : new java.util.TreeSet<String>(keys)) {
                    String a = old.segs.get(key);
                    String b = segs.get(key);
                    if (!Objects.equals(a, b)) {
                        changes.add("notes " + key.replace('|', '/') + ": "
                            + (a == null ? "added" : b == null ? "removed" : "changed"));
                    }
                }
            }
            return changes;
        }

        private static void add(List<String> changes, String field, String a, String b) {
            if (!Objects.equals(a, b)) {
                changes.add(field + ": " + (a == null ? "—" : a) + " → " + (b == null ? "—" : b));
            }
        }
    }

    /** Snapshot of a language or source: the owner of notes that is not a word. */
    static final class Owner {
        String kind;
        String id;
        String name;
        final Map<String, String> segs = new LinkedHashMap<String, String>();

        String key() {
            return kind + "|" + id;
        }
    }

    /** A place where an English string of a table is used: for context in tasks. */
    static final class Use {
        final String ctx;
        final String l;
        final String v;

        Use(String ctx, String l, String v) {
            this.ctx = ctx;
            this.l = l;
            this.v = v;
        }
    }

    /** Usages of an English string of a table. */
    static final class Uses {
        int count;
        final List<Use> sample = new ArrayList<Use>(3);
        final Set<String> langs = new HashSet<String>();

        void add(Use use) {
            count++;
            if (use.l != null) {
                langs.add(use.l);
            }
            if (sample.size() < 3) {
                sample.add(use);
            }
        }
    }

    /** A segment of English notes. */
    static final class NoteUnit {
        String owner;
        String id;
        String part;
        String seg;
        String text;
        String hash;
        /** language of the owning word, for filtering. */
        String l;
        /** headword or name of the owner, for context. */
        String label;

        String key() {
            return noteKey(owner, id, part, seg);
        }
    }

    /** A translated notes segment of the Russian base. */
    static final class NoteEntry {
        String owner;
        String id;
        String part;
        String seg;
        String hash;
        String en;
        String ru;

        String key() {
            return noteKey(owner, id, part, seg);
        }
    }

    /** A per-page gloss translation overriding the gloss table. */
    static final class Override {
        String pageId;
        String field;
        String en;
        String ru;

        String key() {
            return pageId + "|" + field;
        }
    }
}
