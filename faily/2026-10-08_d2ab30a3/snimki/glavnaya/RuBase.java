package xdb.l10n;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import xdb.l10n.Model.NoteEntry;
import xdb.l10n.Model.Override;
import xdb.l10n.Model.Owner;
import xdb.l10n.Model.Page;

/**
 * The translation base of one language (eldamo-data-ru.xml).
 *
 * <pre>
 * &lt;l10n lang="ru" base-version="0.8.13" snapshot="..." synced="..."&gt;
 *   &lt;snapshot&gt;                      the English base at the last synchronization
 *     &lt;p id="page-id" l="q" v="..." sp="n" g="gloss" ng="ngloss"&gt;&lt;s part="notes" seg="lead" h="hash"/&gt;&lt;/p&gt;
 *     &lt;owner kind="language" id="q" name="Quenya"&gt;&lt;s .../&gt;&lt;/owner&gt;
 *   &lt;/snapshot&gt;
 *   &lt;table name="gloss"&gt;&lt;e en="king"&gt;король&lt;/e&gt;&lt;e en="queen"/&gt;&lt;/table&gt;   also title, phrase, label
 *   &lt;overrides&gt;&lt;gloss page-id="..." en="fair"&gt;прекрасный&lt;/gloss&gt;&lt;/overrides&gt;    also ngloss
 *   &lt;notes&gt;&lt;n owner="word" id="page-id" part="notes" seg="lead" hash="..."&gt;&lt;en&gt;..&lt;/en&gt;&lt;ru&gt;..&lt;/ru&gt;&lt;/n&gt;&lt;/notes&gt;
 * &lt;/l10n&gt;
 * </pre>
 * <p>
 * An empty table entry is a known, untranslated string. Notes segments are stored only once
 * translated, together with the English text they were translated from.
 * </p>
 */
final class RuBase {
    String lang = "ru";
    String baseVersion;
    String snapshotId;
    String synced;
    final Map<String, Page> pages = new LinkedHashMap<String, Page>();
    final Map<String, Owner> owners = new LinkedHashMap<String, Owner>();
    final Map<String, TreeMap<String, String>> tables = new LinkedHashMap<String, TreeMap<String, String>>();
    final TreeMap<String, Override> overrides = new TreeMap<String, Override>();
    final TreeMap<String, NoteEntry> notes = new TreeMap<String, NoteEntry>();

    RuBase() {
        for (String table : Model.TABLES) {
            tables.put(table, new TreeMap<String, String>());
        }
    }

    static RuBase read(File file) throws IOException {
        RuBase base = new RuBase();
        try (InputStream in = XmlIO.open(file)) {
            XMLStreamReader r = XmlIO.reader(in);
            String table = null;
            Page page = null;
            Owner owner = null;
            NoteEntry note = null;
            while (r.hasNext()) {
                int event = r.next();
                if (event == XMLStreamConstants.START_ELEMENT) {
                    String name = r.getLocalName();
                    Map<String, String> a = XmlIO.attributes(r);
                    if (name.equals("l10n")) {
                        base.lang = a.get("lang");
                        base.baseVersion = a.get("base-version");
                        base.snapshotId = a.get("snapshot");
                        base.synced = a.get("synced");
                    } else if (name.equals("p")) {
                        page = readPage(a);
                        base.pages.put(page.id, page);
                    } else if (name.equals("owner")) {
                        owner = new Owner();
                        owner.kind = a.get("kind");
                        owner.id = a.get("id");
                        owner.name = a.get("name");
                        base.owners.put(owner.key(), owner);
                    } else if (name.equals("s")) {
                        Map<String, String> segs = page != null ? page.segs : owner != null ? owner.segs : null;
                        if (segs != null) {
                            segs.put(a.get("part") + "|" + a.get("seg"), a.get("h"));
                        }
                    } else if (name.equals("table")) {
                        table = a.get("name");
                        if (!base.tables.containsKey(table)) {
                            base.tables.put(table, new TreeMap<String, String>());
                        }
                    } else if (name.equals("e") && table != null) {
                        base.tables.get(table).put(a.get("en"), XmlIO.text(r).trim());
                    } else if ((name.equals("gloss") || name.equals("ngloss")) && a.containsKey("page-id")) {
                        Override o = new Override();
                        o.pageId = a.get("page-id");
                        o.field = name;
                        o.en = a.get("en");
                        o.ru = XmlIO.text(r).trim();
                        base.overrides.put(o.key(), o);
                    } else if (name.equals("n")) {
                        note = new NoteEntry();
                        note.owner = a.get("owner");
                        note.id = a.get("id");
                        note.part = a.get("part");
                        note.seg = a.get("seg");
                        note.hash = a.get("hash");
                    } else if (name.equals("en") && note != null) {
                        note.en = XmlIO.text(r);
                    } else if (name.equals("ru") && note != null) {
                        note.ru = XmlIO.text(r);
                    }
                } else if (event == XMLStreamConstants.END_ELEMENT) {
                    String name = r.getLocalName();
                    if (name.equals("p")) {
                        page = null;
                    } else if (name.equals("owner")) {
                        owner = null;
                    } else if (name.equals("table")) {
                        table = null;
                    } else if (name.equals("n") && note != null) {
                        base.notes.put(note.key(), note);
                        note = null;
                    }
                }
            }
        } catch (XMLStreamException ex) {
            throw new IOException("Cannot read " + file + ": " + ex.getMessage(), ex);
        }
        return base;
    }

    static Page readPage(Map<String, String> a) {
        Page page = new Page();
        page.id = a.get("id");
        page.l = a.get("l");
        page.v = a.get("v");
        page.speech = a.get("sp");
        page.gloss = a.get("g");
        page.ngloss = a.get("ng");
        return page;
    }

    static String pageXml(Page p, String indent, String extraAttrs) {
        StringBuilder sb = new StringBuilder();
        sb.append(indent).append("<p").append(XmlIO.attr("id", p.id)).append(XmlIO.attr("l", p.l))
            .append(XmlIO.attr("v", p.v)).append(XmlIO.attr("sp", p.speech)).append(XmlIO.attr("g", p.gloss))
            .append(XmlIO.attr("ng", p.ngloss)).append(extraAttrs == null ? "" : extraAttrs);
        if (p.segs.isEmpty()) {
            sb.append("/>\n");
        } else {
            sb.append(">");
            segsXml(sb, p.segs);
            sb.append("</p>\n");
        }
        return sb.toString();
    }

    static String ownerXml(Owner o, String indent) {
        StringBuilder sb = new StringBuilder();
        sb.append(indent).append("<owner").append(XmlIO.attr("kind", o.kind)).append(XmlIO.attr("id", o.id))
            .append(XmlIO.attr("name", o.name));
        if (o.segs.isEmpty()) {
            sb.append("/>\n");
        } else {
            sb.append(">");
            segsXml(sb, o.segs);
            sb.append("</owner>\n");
        }
        return sb.toString();
    }

    private static void segsXml(StringBuilder sb, Map<String, String> segs) {
        for (Map.Entry<String, String> s : segs.entrySet()) {
            int bar = s.getKey().indexOf('|');
            sb.append("<s").append(XmlIO.attr("part", s.getKey().substring(0, bar)))
                .append(XmlIO.attr("seg", s.getKey().substring(bar + 1))).append(XmlIO.attr("h", s.getValue()))
                .append("/>");
        }
    }

    void write(File file) throws IOException {
        try (XmlIO.Out out = new XmlIO.Out(file)) {
            out.raw("<!-- Translation base for Eldamo. Edit translations here or through tasks;\n"
                + "     see L10N-ru.md. The snapshot section is maintained by the tools. -->\n");
            out.raw("<l10n" + XmlIO.attr("lang", lang) + XmlIO.attr("base-version", baseVersion)
                + XmlIO.attr("snapshot", snapshotId) + XmlIO.attr("synced", synced) + ">\n");
            out.raw("  <snapshot>\n");
            for (Page p : pages.values()) {
                out.raw(pageXml(p, "    ", null));
            }
            for (Owner o : owners.values()) {
                out.raw(ownerXml(o, "    "));
            }
            out.raw("  </snapshot>\n");
            for (Map.Entry<String, TreeMap<String, String>> table : tables.entrySet()) {
                out.raw("  <table" + XmlIO.attr("name", table.getKey()) + ">\n");
                for (Map.Entry<String, String> e : table.getValue().entrySet()) {
                    String ru = e.getValue();
                    out.raw("    <e" + XmlIO.attr("en", e.getKey())
                        + (ru == null || ru.isEmpty() ? "/>\n" : ">" + XmlIO.escText(ru) + "</e>\n"));
                }
                out.raw("  </table>\n");
            }
            out.raw("  <overrides>\n");
            for (Override o : overrides.values()) {
                out.raw("    <" + o.field + XmlIO.attr("page-id", o.pageId) + XmlIO.attr("en", o.en) + ">"
                    + XmlIO.escText(o.ru == null ? "" : o.ru) + "</" + o.field + ">\n");
            }
            out.raw("  </overrides>\n");
            out.raw("  <notes>\n");
            for (NoteEntry n : notes.values()) {
                out.raw("    <n" + XmlIO.attr("owner", n.owner) + XmlIO.attr("id", n.id) + XmlIO.attr("part", n.part)
                    + XmlIO.attr("seg", n.seg) + XmlIO.attr("hash", n.hash) + ">\n");
                out.raw("      <en>" + XmlIO.cdata(n.en == null ? "" : n.en) + "</en>\n");
                out.raw("      <ru>" + XmlIO.cdata(n.ru == null ? "" : n.ru) + "</ru>\n");
                out.raw("    </n>\n");
            }
            out.raw("  </notes>\n");
            out.raw("</l10n>\n");
        }
    }

    /** Replace the snapshot by the state of an English base. */
    void takeSnapshot(EnglishBase en) {
        pages.clear();
        pages.putAll(en.pages);
        owners.clear();
        owners.putAll(en.owners);
        baseVersion = en.version;
        snapshotId = en.snapshotId();
    }
}
