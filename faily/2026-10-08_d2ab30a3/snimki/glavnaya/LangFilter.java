package xdb.control;

import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Set;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Interface language selected by a URI prefix: "/ru/content/..." is served as "/content/..." with
 * the request attribute {@link #UI_LANG} set to "ru". All links in the generated pages are
 * relative, so the prefix carries over to every page reached from there, and crawling
 * "/ru/pub/index.html" yields a separate static site in that language. Requests without a prefix
 * are unchanged (English).
 *
 * <p>
 * The supported languages are given by the "languages" init parameter (comma separated). The
 * filter is mapped for both REQUEST and FORWARD dispatches, so it combines with PubModeFilter in
 * either order ("/ru/pub/..." or "/pub/ru/...").
 * </p>
 */
public class LangFilter implements Filter {

    /** Request attribute holding the interface language. */
    public static final String UI_LANG = "UI_LANG";

    /** The default interface language, used when no prefix is present. */
    public static final String DEFAULT_LANG = "en";

    private Set<String> languages = Collections.emptySet();

    @Override
    public void init(FilterConfig config) throws ServletException {
        String param = config.getInitParameter("languages");
        if (param != null) {
            Set<String> set = new LinkedHashSet<String>();
            for (String lang : Arrays.asList(param.split(","))) {
                lang = lang.trim();
                if (lang.matches("[a-z]{2,3}") && !DEFAULT_LANG.equals(lang)) {
                    set.add(lang);
                }
            }
            languages = Collections.unmodifiableSet(set);
        }
    }

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
        throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        String context = request.getContextPath();
        String path = request.getRequestURI().substring(context.length());
        String lang = prefixLanguage(path);
        if (lang == null) {
            chain.doFilter(req, res);
            return;
        }
        String rest = path.substring(lang.length() + 1);
        if (rest.length() == 0) {
            ((HttpServletResponse) res).sendRedirect(context + "/" + lang + "/");
            return;
        }
        request.setAttribute(UI_LANG, lang);
        request.getRequestDispatcher(rest).forward(req, res);
    }

    private String prefixLanguage(String path) {
        if (!path.startsWith("/")) {
            return null;
        }
        int end = path.indexOf('/', 1);
        String segment = end < 0 ? path.substring(1) : path.substring(1, end);
        return languages.contains(segment) ? segment : null;
    }

    /**
     * The interface language of a request.
     *
     * @param request
     *            The request.
     * @return The language code, "en" by default.
     */
    public static String getLanguage(ServletRequest request) {
        Object lang = request.getAttribute(UI_LANG);
        return lang == null ? DEFAULT_LANG : lang.toString();
    }

    @Override
    public void destroy() {
    }
}
