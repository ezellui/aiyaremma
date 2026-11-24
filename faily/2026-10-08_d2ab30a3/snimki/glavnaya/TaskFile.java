package xdb.l10n;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

import xdb.l10n.Model.Owner;
import xdb.l10n.Model.Page;
import xdb.l10n.Model.Use;

/**
 * A translation task: the units to translate, with context, and the changes of the English base
 * since the last synchronization of the Russian base.
 *
 * <pre>
 * &lt;task lang="ru" base-version=".." from-snapshot=".." to-snapshot=".." created=".." scope="delta"&gt;
 *   &lt;summary&gt;...&lt;/summary&gt;
 *   &lt;pages-added&gt;&lt;p .../&gt;&lt;/pages-added&gt;
 *   &lt;pages-removed&gt;&lt;p .../&gt;&lt;/pages-removed&gt;
 *   &lt;pages-changed&gt;&lt;p ... &gt;&lt;change&gt;gloss: old → new&lt;/change&gt;&lt;/p&gt;&lt;/pages-changed&gt;
 *   &lt;owners-changed&gt;&lt;owner .../&gt;&lt;/owners-changed&gt;  &lt;owners-removed&gt;...&lt;/owners-removed&gt;
 *   &lt;item kind="gloss" status="new" en="king"&gt;
 *     &lt;use ctx="page-id" l="q" v="aran"/&gt; &lt;hint .../&gt;
 *     &lt;ru&gt;&lt;/ru&gt;                      the translation goes here
 *     &lt;override page-id=".."&gt;..&lt;/override&gt;   optional: a different translation for one page
 *   &lt;/item&gt;
 *   &lt;item kind="notes" status="changed" owner="word" id=".." part="notes" seg="lead" hash=".."&gt;
 *     &lt;context .../&gt; &lt;en&gt;..&lt;/en&gt; &lt;old-en&gt;..&lt;/old-en&gt; &lt;old-ru&gt;..&lt;/old-ru&gt; &lt;ru&gt;..&lt;/ru&gt;
 *   &lt;/item&gt;
 *   &lt;orphan .../&gt;
 * &lt;/task&gt;
 * </pre>
 */
final class TaskFile {
    String lang;
    String baseVersion;
    String fromSnapshot;
    String toSnapshot;
    String created;
    String scope;
    String filters;
    String summary;
    final List<Page> added = new ArrayList<Page>();
    final List<Page> removed = new ArrayList<Page>();
    final List<Page> changed = new ArrayList<Page>();
    final Map<String, List<String>> changes = new LinkedHashMap<String, List<String>>();
    final List<Owner> ownersChanged = new ArrayList<Owner>();
    final List<Owner> ownersRemoved = new ArrayList<Owner>();
    final List<Item> items = new ArrayList<Item>();
    final List<Item> orphans = new ArrayList<Item>();

    /** A unit to translate. */
    static final class Item {
        String kind;
        String status;
        String en;
        String pageId;
        String field;
        String owner;
        String id;
        String part;
        String seg;
        String hash;
        String context;
        String oldEn;
        String oldRu;
        String ru;
        final List<Use> uses = new ArrayList<Use>();
        final List<String[]> hints = new ArrayList<String[]>();
        /** page-id -> per-page translation given in the task. */
        final Map<String, String> overrides = new LinkedHashMap<String, String>();

        boolean isNotes() {
            return "notes".equals(kind);
        }

        String label() {
            if (isNotes()) {
                return owner + " " + id + " " + part + "/" + seg + (context == null ? "" : " (" + context + ")");
            } else if ("gloss-override".equals(kind)) {
                return "gloss " + field + " of page " + pageId + ": " + en;
            }
            return kind + ": " + en;
        }
    }

    void write(File file) throws IOException {
        try (XmlIO.Out out = new XmlIO.Out(file)) {
            out.raw("<!-- Translation task for Eldamo. Fill in every <ru> element (and optionally add\n"
                + "     <override page-id=\"...\">...</override> to a gloss item), then run the apply\n"
                + "     command. Keep the markers *, ?, ⚠️, [..], {..} and the HTML of notes. -->\n");
            out.raw("<task" + XmlIO.attr("lang", lang) + XmlIO.attr("base-version", baseVersion)
                + XmlIO.attr("from-snapshot", fromSnapshot) + XmlIO.attr("to-snapshot", toSnapshot)
                + XmlIO.attr("created", created) + XmlIO.attr("scope", scope) + XmlIO.attr("filters", filters) + ">\n");
            out.raw("  <summary>" + XmlIO.escText(summary == null ? "" : summary) + "</summary>\n");
            writePages(out, "pages-added", added);
            writePages(out, "pages-removed", removed);
            writePages(out, "pages-changed", changed);
            writeOwners(out, "owners-changed", ownersChanged);
            writeOwners(out, "owners-removed", ownersRemoved);
            for (Item item : items) {
                writeItem(out, item, "item");
            }
            for (Item item : orphans) {
                writeItem(out, item, "orphan");
            }
            out.raw("</task>\n");
        }
    }

    private void writePages(XmlIO.Out out, String name, List<Page> pages) throws IOException {
        out.raw("  <" + name + XmlIO.attr("count", String.valueOf(pages.size())) + ">\n");
        for (Page p : pages) {
            List<String> list = changes.get(p.id);
            if (list == null || !name.equals("pages-changed")) {
                out.raw(RuBase.pageXml(p, "    ", null));
            } else {
                // the new state of the page, with a readable list of changes
                String xml = RuBase.pageXml(p, "    ", null);
                StringBuilder ch = new StringBuilder();
                for (String c : list) {
                    ch.append("<change>").append(XmlIO.escText(c)).append("</change>");
                }
                if (xml.endsWith("/>\n")) {
                    xml = xml.substring(0, xml.length() - 3) + ">" + ch + "</p>\n";
                } else {
                    xml = xml.substring(0, xml.length() - 5) + ch + "</p>\n";
                }
                out.raw(xml);
            }
        }
        out.raw("  </" + name + ">\n");
    }

    private void writeOwners(XmlIO.Out out, String name, List<Owner> owners) throws IOException {
        out.raw("  <" + name + XmlIO.attr("count", String.valueOf(owners.size())) + ">\n");
        for (Owner o : owners) {
            out.raw(RuBase.ownerXml(o, "    "));
        }
        out.raw("  </" + name + ">\n");
    }

    private void writeItem(XmlIO.Out out, Item i, String element) throws IOException {
        out.raw("  <" + element + XmlIO.attr("kind", i.kind) + XmlIO.attr("status", i.status)
            + XmlIO.attr("owner", i.owner) + XmlIO.attr("id", i.id) + XmlIO.attr("part", i.part)
            + XmlIO.attr("seg", i.seg) + XmlIO.attr("hash", i.hash) + XmlIO.attr("page-id", i.pageId)
            + XmlIO.attr("field", i.field) + (i.isNotes() ? "" : XmlIO.attr("en", i.en)) + ">\n");
        if (i.context != null) {
            out.raw("    <context>" + XmlIO.escText(i.context) + "</context>\n");
        }
        for (Use u : i.uses) {
            out.raw("    <use" + XmlIO.attr("ctx", u.ctx) + XmlIO.attr("l", u.l) + XmlIO.attr("v", u.v) + "/>\n");
        }
        for (String[] h : i.hints) {
            out.raw("    <hint" + XmlIO.attr("page-id", h[0]) + XmlIO.attr("old-en", h[1]) + ">"
                + XmlIO.escText(h[2]) + "</hint>\n");
        }
        if (i.isNotes()) {
            out.raw("    <en>" + XmlIO.cdata(i.en == null ? "" : i.en) + "</en>\n");
            if (i.oldEn != null) {
                out.raw("    <old-en>" + XmlIO.cdata(i.oldEn) + "</old-en>\n");
            }
            if (i.oldRu != null) {
                out.raw("    <old-ru>" + XmlIO.cdata(i.oldRu) + "</old-ru>\n");
            }
            if (!element.equals("orphan")) {
                out.raw("    <ru>" + XmlIO.cdata(i.ru == null ? "" : i.ru) + "</ru>\n");
            }
        } else {
            if (i.oldEn != null) {
                out.raw("    <old-en>" + XmlIO.escText(i.oldEn) + "</old-en>\n");
            }
            if (i.oldRu != null) {
                out.raw("    <old-ru>" + XmlIO.escText(i.oldRu) + "</old-ru>\n");
            }
            if (!element.equals("orphan")) {
                out.raw("    <ru>" + XmlIO.escText(i.ru == null ? "" : i.ru) + "</ru>\n");
            }
            for (Map.Entry<String, String> o : i.overrides.entrySet()) {
                out.raw("    <override" + XmlIO.attr("page-id", o.getKey()) + ">" + XmlIO.escText(o.getValue())
                    + "</override>\n");
            }
        }
        out.raw("  </" + element + ">\n");
    }

    static TaskFile read(File file) throws IOException {
        TaskFile task = new TaskFile();
        try (InputStream in = XmlIO.open(file)) {
            XMLStreamReader r = XmlIO.reader(in);
            String section = null;
            Item item = null;
            Page page = null;
            Owner owner = null;
            while (r.hasNext()) {
                int event = r.next();
                if (event == XMLStreamConstants.START_ELEMENT) {
                    String name = r.getLocalName();
                    Map<String, String> a = XmlIO.attributes(r);
                    if (name.equals("task")) {
                        task.lang = a.get("lang");
                        task.baseVersion = a.get("base-version");
                        task.fromSnapshot = a.get("from-snapshot");
                        task.toSnapshot = a.get("to-snapshot");
                        task.created = a.get("created");
                        task.scope = a.get("scope");
                        task.filters = a.get("filters");
                    } else if (name.startsWith("pages-") || name.startsWith("owners-")) {
                        section = name;
                    } else if (name.equals("p") && section != null) {
                        page = RuBase.readPage(a);
                        if (section.equals("pages-added")) {
                            task.added.add(page);
                        } else if (section.equals("pages-removed")) {
                            task.removed.add(page);
                        } else {
                            task.changed.add(page);
                        }
                    } else if (name.equals("owner") && section != null) {
                        owner = new Owner();
                        owner.kind = a.get("kind");
                        owner.id = a.get("id");
                        owner.name = a.get("name");
                        (section.equals("owners-removed") ? task.ownersRemoved : task.ownersChanged).add(owner);
                    } else if (name.equals("s")) {
                        Map<String, String> segs = page != null ? page.segs : owner != null ? owner.segs : null;
                        if (segs != null) {
                            segs.put(a.get("part") + "|" + a.get("seg"), a.get("h"));
                        }
                    } else if (name.equals("change") && page != null) {
                        List<String> list = task.changes.get(page.id);
                        if (list == null) {
                            list = new ArrayList<String>();
                            task.changes.put(page.id, list);
                        }
                        list.add(XmlIO.text(r));
                    } else if (name.equals("item") || name.equals("orphan")) {
                        item = new Item();
                        item.kind = a.get("kind");
                        item.status = a.get("status");
                        item.en = a.get("en");
                        item.pageId = a.get("page-id");
                        item.field = a.get("field");
                        item.owner = a.get("owner");
                        item.id = a.get("id");
                        item.part = a.get("part");
                        item.seg = a.get("seg");
                        item.hash = a.get("hash");
                        (name.equals("item") ? task.items : task.orphans).add(item);
                    } else if (item != null) {
                        if (name.equals("context")) {
                            item.context = XmlIO.text(r);
                        } else if (name.equals("use")) {
                            item.uses.add(new Use(a.get("ctx"), a.get("l"), a.get("v")));
                        } else if (name.equals("hint")) {
                            item.hints.add(new String[] {a.get("page-id"), a.get("old-en"), XmlIO.text(r)});
                        } else if (name.equals("en")) {
                            item.en = XmlIO.text(r);
                        } else if (name.equals("old-en")) {
                            item.oldEn = XmlIO.text(r);
                        } else if (name.equals("old-ru")) {
                            item.oldRu = XmlIO.text(r);
                        } else if (name.equals("ru")) {
                            item.ru = XmlIO.text(r);
                        } else if (name.equals("override")) {
                            item.overrides.put(a.get("page-id"), XmlIO.text(r).trim());
                        }
                    }
                } else if (event == XMLStreamConstants.END_ELEMENT) {
                    String name = r.getLocalName();
                    if (name.equals("p")) {
                        page = null;
                    } else if (name.equals("owner")) {
                        owner = null;
                    } else if (name.startsWith("pages-") || name.startsWith("owners-")) {
                        section = null;
                    } else if (name.equals("item") || name.equals("orphan")) {
                        item = null;
                    } else if (name.equals("summary")) {
                        // summary text is informational
                    }
                }
            }
        } catch (XMLStreamException ex) {
            throw new IOException("Cannot read " + file + ": " + ex.getMessage(), ex);
        }
        return task;
    }
}
