package xdb.l10n;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Translated static pages (WEB/l10n/LANG/...): which English pages changed since they were
 * translated.
 *
 * <p>
 * For every translated page the English text it was translated from is kept as
 * WEB/l10n/LANG/sources/PATH.txt, one text block (paragraph, list item, heading, table row) per
 * line. The check compares these blocks with the current English page and lists what changed.
 * After the translation is brought up to date, the current English text is recorded with
 * {@code --accept}.
 * </p>
 */
final class StaticPages {

    private static final Pattern BLOCK = Pattern.compile("(?=<(?:p|li|h[1-6]|tr|dt|dd|table|ul|ol)\\b)",
        Pattern.CASE_INSENSITIVE);
    private static final List<String> SKIP_DIRS = Arrays.asList("l10n", "WEB-INF", "config", "data", "content",
        "layout", "css", "js");

    private final File web;
    private final File root;
    private final File sources;

    StaticPages(File web, String lang) {
        this.web = web;
        this.root = new File(web, "l10n/" + lang);
        this.sources = new File(root, "sources");
    }

    /** Paths (relative, with "/") of the translated pages. */
    List<String> translated() {
        List<String> result = new ArrayList<String>();
        collect(root, "", result, true);
        Collections.sort(result);
        return result;
    }

    /** Paths of the English static pages without a translation. */
    List<String> untranslated() {
        List<String> all = new ArrayList<String>();
        collect(web, "", all, false);
        all.removeAll(translated());
        Collections.sort(all);
        return all;
    }

    private void collect(File dir, String prefix, List<String> result, boolean translations) {
        File[] files = dir.listFiles();
        if (files == null) {
            return;
        }
        for (File f : files) {
            String path = prefix + f.getName();
            if (f.isDirectory()) {
                if (translations ? f.equals(sources) : SKIP_DIRS.contains(f.getName()) && prefix.isEmpty()) {
                    continue;
                }
                collect(f, path + "/", result, translations);
            } else if (f.getName().endsWith(".html") || (f.getName().equals("index.jsp") && prefix.isEmpty())) {
                result.add(path);
            }
        }
    }

    File english(String path) {
        return new File(web, path);
    }

    File source(String path) {
        return new File(sources, path + ".txt");
    }

    /** The text blocks of a page. */
    static List<String> blocks(String html) {
        String s = html.replace("\r", "");
        s = s.replaceAll("(?s)<script.*?</script>|<!--.*?-->|<%--.*?--%>|<%.*?%>", " ");
        List<String> result = new ArrayList<String>();
        for (String block : BLOCK.split(s)) {
            String text = plain(block);
            if (!text.isEmpty()) {
                result.add(text);
            }
        }
        return result;
    }

    private static String plain(String block) {
        String t = block.replaceAll("<[^>]*>", " ");
        t = t.replace("&nbsp;", " ").replace("&#160;", " ").replace("&mdash;", "—").replace("&ndash;", "–")
            .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&amp;", "&");
        Matcher m = Pattern.compile("&#(\\d+);").matcher(t);
        StringBuffer sb = new StringBuffer();
        while (m.find()) {
            m.appendReplacement(sb, Matcher.quoteReplacement(new String(Character.toChars(Integer.parseInt(m.group(1))))));
        }
        m.appendTail(sb);
        return sb.toString().replaceAll("\\s+", " ").trim();
    }

    static String read(File f) throws IOException {
        return new String(Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
    }

    /** Record the English text a translation corresponds to. */
    void accept(String path, File englishFile) throws IOException {
        List<String> blocks = blocks(read(englishFile));
        File target = source(path);
        target.getParentFile().mkdirs();
        StringBuilder sb = new StringBuilder();
        for (String b : blocks) {
            sb.append(b).append('\n');
        }
        Files.write(target.toPath(), sb.toString().getBytes(StandardCharsets.UTF_8));
    }

    /** A change: blocks of the recorded English text replaced by blocks of the current one. */
    static final class Change {
        final List<String> before;
        final List<String> after;

        Change(List<String> before, List<String> after) {
            this.before = before;
            this.after = after;
        }
    }

    /** Differences between two lists of blocks (longest common subsequence). */
    static List<Change> diff(List<String> a, List<String> b) {
        int n = a.size();
        int m = b.size();
        int[][] lcs = new int[n + 1][m + 1];
        for (int i = n - 1; i >= 0; i--) {
            for (int j = m - 1; j >= 0; j--) {
                lcs[i][j] = a.get(i).equals(b.get(j)) ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
            }
        }
        List<Change> changes = new ArrayList<Change>();
        List<String> before = new ArrayList<String>();
        List<String> after = new ArrayList<String>();
        int i = 0;
        int j = 0;
        while (i < n || j < m) {
            if (i < n && j < m && a.get(i).equals(b.get(j))) {
                if (!before.isEmpty() || !after.isEmpty()) {
                    changes.add(new Change(before, after));
                    before = new ArrayList<String>();
                    after = new ArrayList<String>();
                }
                i++;
                j++;
            } else if (j < m && (i == n || lcs[i][j + 1] >= lcs[i + 1][j])) {
                after.add(b.get(j++));
            } else {
                before.add(a.get(i++));
            }
        }
        if (!before.isEmpty() || !after.isEmpty()) {
            changes.add(new Change(before, after));
        }
        return changes;
    }

    /**
     * Report the state of the translated pages.
     *
     * @return The number of pages that need attention.
     */
    int check(PrintStream o, boolean details, boolean listUntranslated) throws IOException {
        int problems = 0;
        List<String> pages = translated();
        o.println("Переведённых статических страниц: " + pages.size() + " (" + root + ")");
        for (String path : pages) {
            File en = english(path);
            File src = source(path);
            if (!en.isFile()) {
                o.println("  " + path + ": английской страницы больше нет");
                problems++;
            } else if (!src.isFile()) {
                o.println("  " + path + ": не записан английский текст, с которого сделан перевод (pages --accept " + path + ")");
                problems++;
            } else {
                List<String> was = Arrays.asList(read(src).split("\n", -1));
                was = new ArrayList<String>(was);
                while (!was.isEmpty() && was.get(was.size() - 1).isEmpty()) {
                    was.remove(was.size() - 1);
                }
                List<Change> changes = diff(was, blocks(read(en)));
                if (changes.isEmpty()) {
                    continue;
                }
                problems++;
                o.println("  " + path + ": английский текст изменился, мест: " + changes.size());
                if (details) {
                    for (Change c : changes) {
                        o.println("    было:  " + (c.before.isEmpty() ? "—" : shorten(String.join(" / ", c.before))));
                        o.println("    стало: " + (c.after.isEmpty() ? "—" : shorten(String.join(" / ", c.after))));
                    }
                }
            }
        }
        if (problems == 0) {
            o.println("Все переведённые страницы соответствуют текущим английским.");
        }
        if (listUntranslated) {
            List<String> rest = untranslated();
            o.println("Статических страниц без перевода: " + rest.size());
            for (String path : rest) {
                o.println("  " + path);
            }
        }
        return problems;
    }

    private static String shorten(String s) {
        return s.length() > 700 ? s.substring(0, 697) + "…" : s;
    }
}
