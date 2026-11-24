package xdb.l10n;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Checks of a translation against its English original: is it translated at all, are there English
 * fragments left in it, are the editorial markers, links, source references and HTML preserved.
 */
final class Checks {

    private Checks() {
    }

    /** A translation that deliberately keeps the English text. */
    static final String SAME_AS_ENGLISH = "=";

    /** Problem codes, in report order. */
    static final List<String> CODES = Collections.unmodifiableList(Arrays.asList(
        "missing", "empty", "same", "latin", "fragment", "markers", "html", "links", "refs", "not-updated",
        "stale", "orphan"));

    static String describe(String code) {
        switch (code) {
            case "empty": return "не переведено (пусто)";
            case "same": return "перевод совпадает с английским";
            case "latin": return "нет ни одной кириллической буквы";
            case "fragment": return "остались английские фрагменты";
            case "markers": return "не совпадают пометы (* ? ⚠️ † ‽ […] {…} (lit.) метки языков)";
            case "html": return "разбалансирована HTML-разметка";
            case "links": return "не совпадают ссылки на статьи <a l v>";
            case "refs": return "не совпадают ссылки на источники";
            case "not-updated": return "изменённый оригинал, а перевод оставлен прежним";
            case "missing": return "строки нет в русской базе (новая в английской)";
            case "stale": return "английский оригинал изменился после перевода";
            case "orphan": return "перевод того, чего больше нет в английской базе";
            default: return code;
        }
    }

    private static final Pattern TAG = Pattern.compile("<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*?)(/?)>");
    private static final Pattern LINK = Pattern.compile("<a\\s[^>]*>");
    private static final Pattern ATTR_L = Pattern.compile("\\bl=\"([^\"]*)\"");
    private static final Pattern ATTR_V = Pattern.compile("\\bv=\"([^\"]*)\"");
    private static final Pattern ATTR_HREF = Pattern.compile("\\bhref=\"([^\"]*)\"");
    /** Source references like PE17/72, LotR/1127-8, VT48/31, Ety/KOR. */
    private static final Pattern REF = Pattern.compile("\\b[A-Z][A-Za-z0-9]*\\d*/[0-9A-Za-zÀ-ž][^\\s,;:)\\]]*");
    /** Language tags in neo-glosses: [ᴹQ.], [ᴱ√], [N., S.] */
    private static final Pattern LANG_TAG = Pattern.compile(
        "\\[\\s*[ᴹᴱᴺᴸ]?(?:[A-Z][A-Za-z]*\\.|√|✶)(?:\\s*,\\s*[ᴹᴱᴺᴸ]?(?:[A-Z][A-Za-z]*\\.|√|✶))*\\s*\\]");
    private static final Set<String> VOID = new HashSet<String>(Arrays.asList("br", "hr", "img", "wbr"));
    private static final Set<String> STOP = new HashSet<String>(Arrays.asList(
        "the", "of", "and", "to", "in", "a", "an", "is", "be", "with", "from", "for", "by", "as", "that",
        "this", "it", "or", "on", "at", "was", "were", "which", "are", "not", "but", "its", "his", "her"));

    /**
     * Problems of a translation.
     *
     * @param en
     *            English original.
     * @param ru
     *            Translation (may be empty).
     * @param notes
     *            Whether the texts are notes (HTML).
     * @return Problem codes; empty if none.
     */
    static List<String> check(String en, String ru, boolean notes) {
        List<String> problems = new ArrayList<String>();
        if (ru == null || ru.trim().isEmpty()) {
            problems.add("empty");
            return problems;
        }
        String e = en == null ? "" : en.trim();
        String r = ru.trim();
        if (r.equals(SAME_AS_ENGLISH)) {
            return problems;
        }
        boolean hasLetters = plain(e).matches("(?s).*\\p{IsLatin}{2}.*");
        if (r.equals(e) && hasLetters) {
            problems.add("same");
            return problems;
        }
        String rPlain = plain(r);
        boolean cyrillic = rPlain.matches("(?s).*\\p{IsCyrillic}.*");
        if (!cyrillic && rPlain.matches("(?s).*\\p{IsLatin}{2}.*")) {
            problems.add("latin");
        } else if (englishFragment(rPlain) != null) {
            problems.add("fragment");
        }
        if (!markers(e).equals(markers(r))) {
            problems.add("markers");
        }
        if (notes || e.contains("<")) {
            if (!balanced(r) && balanced(e)) {
                problems.add("html");
            }
            if (!links(e).equals(links(r))) {
                problems.add("links");
            }
        }
        if (notes && !refs(e).equals(refs(r))) {
            problems.add("refs");
        }
        return problems;
    }

    /**
     * Text without markup and without things that legitimately stay in Latin script: Elvish forms
     * in italics or links, source references, language tags and sigla, phonetic brackets.
     */
    static String plain(String s) {
        String t = s;
        t = t.replaceAll("(?s)<i>.*?</i>", " ");
        t = t.replaceAll("(?s)<a\\s[^>]*>.*?</a>", " ");
        t = t.replaceAll("<[^>]+>", " ");
        t = LANG_TAG.matcher(t).replaceAll(" ");
        t = REF.matcher(t).replaceAll(" ");
        t = t.replaceAll("\\[[^\\]\\s]{1,6}\\]", " ");
        t = t.replaceAll("[ᴹᴱᴺᴸ]?\\b[A-Z][A-Za-z]{0,3}\\.", " ");
        t = t.replaceAll("[√✶]\\S*", " ");
        // words with letters outside plain English (Elvish forms without italics)
        t = t.replaceAll("\\S*[À-ɏḀ-ỿ]\\S*", " ");
        return t;
    }

    /** A run of English-looking words: three in a row, or two with a function word. */
    static String englishFragment(String plain) {
        Matcher m = Pattern.compile("[A-Za-z]+(?:[’'][a-z]+)?").matcher(plain);
        List<String> run = new ArrayList<String>();
        int lastEnd = -1;
        while (m.find()) {
            String between = lastEnd < 0 ? "" : plain.substring(lastEnd, m.start());
            if (lastEnd >= 0 && !between.matches("[\\s,;:()\"“”«»-]*")) {
                if (isFragment(run)) {
                    return String.join(" ", run);
                }
                run.clear();
            }
            run.add(m.group());
            lastEnd = m.end();
        }
        return isFragment(run) ? String.join(" ", run) : null;
    }

    private static boolean isFragment(List<String> run) {
        if (run.size() >= 3) {
            return true;
        }
        if (run.size() == 2) {
            for (String w : run) {
                if (STOP.contains(w.toLowerCase())) {
                    return true;
                }
            }
        }
        return false;
    }

    /** Editorial markers that must survive translation. */
    static String markers(String s) {
        String t = s.replaceAll("(?s)<[^>]+>", "");
        StringBuilder sb = new StringBuilder();
        sb.append("*").append(count(t, "*"));
        sb.append(" ?").append(count(t, "?"));
        sb.append(" ⚠").append(count(t, "⚠"));
        sb.append(" †").append(count(t, "†"));
        sb.append(" ‽").append(count(t, "‽"));
        sb.append(" [").append(count(t, "["));
        sb.append(" {").append(count(t, "{"));
        sb.append(" lit").append(count(t, "(lit.)") + count(t, "(букв.)"));
        List<String> tags = new ArrayList<String>();
        Matcher m = LANG_TAG.matcher(t);
        while (m.find()) {
            tags.add(m.group().replaceAll("\\s", ""));
        }
        sb.append(" tags").append(tags);
        return sb.toString();
    }

    private static int count(String s, String sub) {
        int n = 0;
        for (int i = s.indexOf(sub); i >= 0; i = s.indexOf(sub, i + sub.length())) {
            n++;
        }
        return n;
    }

    /** Multiset of word links and other links, as a sorted list. */
    static List<String> links(String s) {
        List<String> result = new ArrayList<String>();
        Matcher m = LINK.matcher(s);
        while (m.find()) {
            String tag = m.group();
            result.add(group(ATTR_L, tag) + "|" + group(ATTR_V, tag) + "|" + group(ATTR_HREF, tag));
        }
        Collections.sort(result);
        return result;
    }

    /** Multiset of source references outside of links, as a sorted list. */
    static List<String> refs(String s) {
        String t = s.replaceAll("<[^>]+>", " ");
        List<String> result = new ArrayList<String>();
        Matcher m = REF.matcher(t);
        while (m.find()) {
            result.add(m.group());
        }
        Collections.sort(result);
        return result;
    }

    private static String group(Pattern p, String s) {
        Matcher m = p.matcher(s);
        return m.find() ? m.group(1) : "";
    }

    /** Whether the HTML tags are properly nested. */
    static boolean balanced(String s) {
        Deque<String> stack = new ArrayDeque<String>();
        Matcher m = TAG.matcher(s);
        while (m.find()) {
            String name = m.group(2).toLowerCase();
            if (VOID.contains(name) || !m.group(4).isEmpty()) {
                continue;
            }
            if (m.group(1).isEmpty()) {
                stack.push(name);
            } else {
                if (stack.isEmpty() || !stack.pop().equals(name)) {
                    return false;
                }
            }
        }
        return stack.isEmpty();
    }
}
