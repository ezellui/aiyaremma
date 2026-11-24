package xdb.l10n;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import xdb.l10n.Model.NoteUnit;
import xdb.l10n.Model.Owner;
import xdb.l10n.Model.Page;
import xdb.l10n.Model.Use;
import xdb.l10n.Model.Uses;

/**
 * The translatable units of the English base (eldamo-data.xml), read in one streaming pass.
 *
 * <p>
 * Texts are taken the way the site shows them: element text is trimmed, and the text of an element
 * that also has child elements is ignored (the site's parser drops it).
 * </p>
 */
final class EnglishBase {
    String version;
    /** page-id -> page, in document order. */
    final Map<String, Page> pages = new LinkedHashMap<String, Page>();
    /** kind|id -> language or source. */
    final Map<String, Owner> owners = new LinkedHashMap<String, Owner>();
    /** table -> English string -> usages. */
    final Map<String, Map<String, Uses>> tables = new LinkedHashMap<String, Map<String, Uses>>();
    /** note key -> segment. */
    final Map<String, NoteUnit> notes = new LinkedHashMap<String, NoteUnit>();

    private EnglishBase() {
        for (String table : Model.TABLES) {
            tables.put(table, new LinkedHashMap<String, Uses>());
        }
    }

    private static final class Frame {
        final String name;
        final Map<String, String> attrs;
        final String l;
        final String speech;
        final String pageId;
        final String source;
        final Frame parent;
        boolean hasChild;
        final StringBuilder text = new StringBuilder();
        final Map<String, Integer> childCounts = new HashMap<String, Integer>();
        int position;

        Frame(String name, Map<String, String> attrs, Frame parent) {
            this.name = name;
            this.attrs = attrs;
            this.parent = parent;
            String ownL = attrs.get("l");
            this.l = ownL != null ? ownL : parent == null ? null : parent.l;
            String ownSpeech = attrs.get("speech");
            this.speech = ownSpeech != null ? ownSpeech : parent == null ? null : parent.speech;
            this.pageId = name.equals("word") ? attrs.get("page-id") : parent == null ? null : parent.pageId;
            this.source = name.equals("ref") ? attrs.get("source") : parent == null ? null : parent.source;
            if (parent != null) {
                parent.hasChild = true;
                Integer n = parent.childCounts.get(name);
                position = n == null ? 1 : n + 1;
                parent.childCounts.put(name, position);
            }
        }
    }

    static EnglishBase read(File file) throws IOException {
        EnglishBase base = new EnglishBase();
        try (InputStream in = XmlIO.open(file)) {
            XMLStreamReader r = XmlIO.reader(in);
            Deque<Frame> stack = new ArrayDeque<Frame>();
            while (r.hasNext()) {
                int event = r.next();
                if (event == XMLStreamConstants.START_ELEMENT) {
                    Frame frame = new Frame(r.getLocalName(), XmlIO.attributes(r), stack.peek());
                    stack.push(frame);
                    base.start(frame);
                } else if (event == XMLStreamConstants.CHARACTERS || event == XMLStreamConstants.CDATA) {
                    Frame frame = stack.peek();
                    if (frame != null) {
                        frame.text.append(r.getText());
                    }
                } else if (event == XMLStreamConstants.END_ELEMENT) {
                    base.end(stack.pop());
                }
            }
        } catch (XMLStreamException ex) {
            throw new IOException("Cannot read " + file + ": " + ex.getMessage(), ex);
        }
        return base;
    }

    private void start(Frame f) {
        Map<String, String> a = f.attrs;
        if (f.name.equals("word-data")) {
            version = a.get("version");
        } else if (f.name.equals("word") && f.pageId != null) {
            Page page = new Page();
            page.id = f.pageId;
            page.l = f.l;
            page.v = a.get("v");
            page.speech = f.speech;
            page.gloss = a.get("gloss");
            page.ngloss = a.get("ngloss");
            pages.put(page.id, page);
            Use use = new Use(page.id, page.l, page.v);
            use(tables.get("gloss"), page.gloss, use);
            use(tables.get("gloss"), page.ngloss, use);
            use(tables.get("title"), page.title(), use);
        } else if (f.name.equals("language") || f.name.equals("source")) {
            Owner owner = new Owner();
            owner.kind = f.name;
            owner.id = f.name.equals("language") ? a.get("id") : a.get("prefix");
            owner.name = a.get("name");
            if (owner.id != null) {
                owners.put(owner.key(), owner);
            }
            if (f.name.equals("language")) {
                use(tables.get("label"), a.get("name"), new Use("language:" + owner.id, owner.id, null));
            }
        } else if (f.name.equals("language-cat")) {
            String id = a.get("id");
            use(tables.get("label"), a.get("name"), new Use("language-cat:" + (id == null ? "" : id), null, null));
        } else if (f.name.equals("cat") || f.name.equals("cat-group")) {
            use(tables.get("label"), a.get("label"), new Use(f.name + ":" + a.get("id"), null, null));
        }
    }

    private void end(Frame f) {
        Frame parent = f.parent;
        if (parent == null) {
            return;
        }
        String part = f.position == 1 ? f.name : f.name + "#" + f.position;
        if (f.name.equals("notes") && parent.name.equals("word") && parent.attrs.get("page-id") != null) {
            Page page = pages.get(parent.pageId);
            addNotes("word", parent.pageId, part, f.text.toString().trim(), page.l,
                page.v, page.segs);
        } else if (parent.name.equals("language") && Model.LANGUAGE_SECTIONS.contains(f.name)) {
            Owner owner = owners.get("language|" + parent.attrs.get("id"));
            if (owner != null) {
                addNotes("language", owner.id, part, f.text.toString().trim(), owner.id, owner.name, owner.segs);
            }
        } else if (f.name.equals("notes") && parent.name.equals("source")) {
            Owner owner = owners.get("source|" + parent.attrs.get("prefix"));
            if (owner != null) {
                addNotes("source", owner.id, part, f.text.toString().trim(), null, owner.name, owner.segs);
            }
        } else if (Model.PHRASE_ELEMENTS.contains(f.name) && !f.hasChild) {
            String text = f.text.toString().trim();
            if (!text.isEmpty() && text.matches("(?s).*\\p{IsLatin}.*")) {
                String ctx = f.source != null ? f.source : f.pageId;
                Page page = f.pageId == null ? null : pages.get(f.pageId);
                use(tables.get("phrase"), text, new Use(ctx, f.l, page == null ? null : page.v));
            }
        }
    }

    private void addNotes(String owner, String id, String part, String text, String l, String label,
        Map<String, String> segs) {
        for (Notes.Segment segment : Notes.split(text)) {
            NoteUnit unit = new NoteUnit();
            unit.owner = owner;
            unit.id = id;
            unit.part = part;
            unit.seg = segment.name;
            unit.text = segment.text.trim();
            unit.hash = Notes.hash(segment.text);
            unit.l = l;
            unit.label = label;
            notes.put(unit.key(), unit);
            segs.put(part + "|" + segment.name, unit.hash);
        }
    }

    private static void use(Map<String, Uses> table, String en, Use use) {
        if (en == null) {
            return;
        }
        en = en.trim();
        if (en.isEmpty() || en.equals("[unglossed]")) {
            return;
        }
        Uses uses = table.get(en);
        if (uses == null) {
            uses = new Uses();
            table.put(en, uses);
        }
        uses.add(use);
    }

    /** Identifier of this state of the English base: a hash of the snapshot data. */
    String snapshotId() {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            for (Page p : pages.values()) {
                update(md, p.id, p.l, p.v, p.speech, p.gloss, p.ngloss, p.segs.toString());
            }
            for (Owner o : owners.values()) {
                update(md, o.kind, o.id, o.name, o.segs.toString());
            }
            for (Map.Entry<String, Map<String, Uses>> table : tables.entrySet()) {
                update(md, table.getKey(), String.valueOf(table.getValue().size()));
            }
            byte[] digest = md.digest();
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 8; i++) {
                sb.append(String.format("%02x", digest[i] & 0xff));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException ex) {
            throw new IllegalStateException(ex);
        }
    }

    private static void update(MessageDigest md, String... values) {
        for (String v : values) {
            md.update((v == null ? "\u0000" : v).getBytes(StandardCharsets.UTF_8));
            md.update((byte) 1);
        }
    }
}
