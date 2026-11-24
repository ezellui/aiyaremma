package xdb.l10n;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Splitting of notes (HTML strings) into independently translatable segments, and hashing of the
 * English text of a segment. The same code is used by the translation tools and at run time, so
 * both always agree on segment names and hashes.
 *
 * <p>
 * Segments, in order:
 * </p>
 * <ul>
 * <li>"lead": the first paragraph, when the notes start with an unheaded paragraph;</li>
 * <li>"main": the rest of the text before the first headed paragraph;</li>
 * <li>a named segment for every paragraph starting with a bold heading, such as
 * {@code <p><b>Conceptual Development:</b>}, up to the next headed paragraph. A repeated heading
 * gets a suffix: "Neo-Quenya#2".</li>
 * </ul>
 * <p>
 * The segments are exact substrings: joining their texts gives back the original string.
 * </p>
 */
public final class Notes {

    /** A headed paragraph: {@code <p><b>Heading:</b>} or {@code <p><b>Heading</b>:}. */
    private static final Pattern HEAD = Pattern.compile("<p>\\s*<b>\\s*([^<]{1,80}?)\\s*:?\\s*</b>");

    private Notes() {
    }

    /** A segment of notes. */
    public static final class Segment {
        public final String name;
        public final String text;

        Segment(String name, String text) {
            this.name = name;
            this.text = text;
        }
    }

    /**
     * Split notes into segments.
     *
     * @param html
     *            The notes.
     * @return The segments; empty for blank notes.
     */
    public static List<Segment> split(String html) {
        List<Segment> result = new ArrayList<Segment>();
        if (html == null || html.trim().isEmpty()) {
            return result;
        }
        List<int[]> heads = new ArrayList<int[]>();
        List<String> names = new ArrayList<String>();
        Matcher m = HEAD.matcher(html);
        while (m.find()) {
            heads.add(new int[] {m.start()});
            names.add(m.group(1).replaceAll("\\s+", " ").trim());
        }
        int firstHead = heads.isEmpty() ? html.length() : heads.get(0)[0];
        String before = html.substring(0, firstHead);
        if (!before.trim().isEmpty()) {
            String trimmed = before.replaceAll("^\\s+", "");
            int end = before.indexOf("</p>");
            if (trimmed.startsWith("<p") && end >= 0) {
                end += 4;
                String rest = before.substring(end);
                if (rest.trim().isEmpty()) {
                    result.add(new Segment("lead", before));
                } else {
                    result.add(new Segment("lead", before.substring(0, end)));
                    result.add(new Segment("main", rest));
                }
            } else {
                result.add(new Segment("lead", before));
            }
        }
        // when only whitespace precedes the first heading, the first section starts at 0
        Map<String, Integer> seen = new HashMap<String, Integer>();
        for (int i = 0; i < heads.size(); i++) {
            int start = (i == 0 && before.trim().isEmpty()) ? 0 : heads.get(i)[0];
            int end = i + 1 < heads.size() ? heads.get(i + 1)[0] : html.length();
            String name = names.get(i);
            Integer n = seen.get(name);
            seen.put(name, n == null ? 1 : n + 1);
            if (n != null) {
                name = name + "#" + (n + 1);
            }
            result.add(new Segment(name, html.substring(start, end)));
        }
        return result;
    }

    /**
     * Hash of the English text of a segment: insensitive to whitespace differences.
     *
     * @param text
     *            The text.
     * @return 12 hex digits of SHA-1.
     */
    public static String hash(String text) {
        String normalized = text == null ? "" : text.replaceAll("\\s+", " ").trim();
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-1");
            byte[] digest = md.digest(normalized.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 6; i++) {
                sb.append(String.format("%02x", digest[i] & 0xff));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException ex) {
            throw new IllegalStateException(ex);
        }
    }

    /**
     * Group of a segment, for selecting parts of the notes in a task: "lead", "main", "cd"
     * (Conceptual Development), "neo" (Neo-Quenya, Neo-Sindarin, Neo-Eldarin...) or "other".
     *
     * @param segment
     *            The segment name.
     * @return The group.
     */
    public static String group(String segment) {
        String base = segment.replaceAll("#\\d+$", "");
        if (base.equals("lead") || base.equals("main")) {
            return base;
        }
        if (base.startsWith("Conceptual Development")) {
            return "cd";
        }
        if (base.startsWith("Neo-")) {
            return "neo";
        }
        return "other";
    }
}
