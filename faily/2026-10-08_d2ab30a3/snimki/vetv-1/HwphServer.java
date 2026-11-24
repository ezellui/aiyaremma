/*
 * HwphServer — the HWPh reader served straight from the XML database, as Eldamo serves its pages:
 * every address is answered by the XQuery file that makes it, at the moment it is asked for.
 *
 *   java -Xmx3g -jar server/hwph-server.jar --db site.xml [--src HWPh_epub] [--port 8000] [--open]
 *
 * The database is loaded once and the queries are compiled once. What a query makes is kept in a
 * cache folder next to the database (a second request is read from disk), and the files that cover
 * the whole dictionary are made in the background right after the start, so that the reader warms up
 * by itself: the article pages at once, the word index group after group.
 *
 * Changes are picked up on the next request: a changed database or query empties the cache; with
 * --src, a changed Markdown volume first runs md2xml.py (that takes a minute or two).
 *
 * Java 8, Saxon-HE 9.9 or newer (s9api), com.sun.net.httpserver of the JDK. No other libraries.
 */
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import net.sf.saxon.s9api.*;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class HwphServer {

    // ------------------------------------------------------------------ settings
    Path home;            // the project folder (xq/, static/, md2xml.py)
    Path db;              // the XML database
    Path src;             // the Markdown volumes (optional: rebuild the database when they change)
    Path img;             // pictures shown as PNG
    Path cacheRoot;
    int port = 8000;
    int parts = 8;
    String lang = "ru";
    String python = "python";
    boolean open;

    static final String PDIR = "HWPH.put(\"pdir\",\n{}\n);\n";   // no word gets a file of its own here
    static final long HEAVY = 1_000_000_000L;

    // ------------------------------------------------------------------ the loaded state
    final Processor proc = new Processor(false);
    final Object reloadLock = new Object();
    volatile Generation gen;
    volatile long lastCheck;

    /** one database + one set of compiled queries; replaced as a whole when anything changes */
    class Generation {
        final XdmNode doc;
        final XQueryExecutable article, index, global, manifest;
        final Path cache;
        final long stamp;
        final ConcurrentHashMap<String, CompletableFuture<Void>> jobs = new ConcurrentHashMap<>();
        final PriorityBlockingQueue<Task> queue = new PriorityBlockingQueue<>();
        final Thread worker;
        volatile boolean closed;
        volatile XdmValue articleIndexes;

        Generation(long stamp) throws Exception {
            this.stamp = stamp;
            long t = System.currentTimeMillis();
            doc = proc.newDocumentBuilder().build(db.toFile());
            log("база загружена: " + db + " (" + secs(t) + ")");
            XQueryCompiler c = proc.newXQueryCompiler();
            Path xq = home.resolve("xq");
            article = c.compile(xq.resolve("article.xq").toFile());
            index = c.compile(xq.resolve("index.xq").toFile());
            global = c.compile(xq.resolve("global.xq").toFile());
            manifest = c.compile(xq.resolve("manifest.xq").toFile());
            cache = cacheRoot.resolve("v" + stamp);
            Files.createDirectories(cache);
            worker = new Thread(this::work, "hwph-worker");
            worker.setDaemon(true);
            worker.start();
            // warming up: what the reader asks for first, then the word index group by group
            background("indexes");
            background("meta");
            background("global");
            for (int g = 0; g < parts; g++) background("part:" + g);
            background("vocab");
        }

        void background(String key) { submit(key, 1); }

        /** the job that makes key, started (or moved ahead) at the given priority (0 = asked for now) */
        CompletableFuture<Void> submit(String key, int priority) {
            CompletableFuture<Void> f = jobs.computeIfAbsent(key, k -> new CompletableFuture<>());
            if (!f.isDone()) queue.add(new Task(key, priority));
            return f;
        }

        void work() {
            while (!closed) {
                Task task;
                try { task = queue.poll(1, TimeUnit.SECONDS); } catch (InterruptedException e) { return; }
                if (task == null || closed) continue;
                runJob(task.key);
            }
        }

        /** runs a job on this thread unless it is done already (the worker is the only runner) */
        void runJob(String key) {
            CompletableFuture<Void> f = jobs.computeIfAbsent(key, k -> new CompletableFuture<>());
            if (f.isDone()) return;
            long t = System.currentTimeMillis();
            try {
                make(key);
                f.complete(null);
                log(key + " (" + secs(t) + ")");
            } catch (Throwable e) {
                f.completeExceptionally(e);
                log(key + ": ОШИБКА " + e);
            }
        }

        void make(String key) throws Exception {
            if (key.equals("indexes")) {
                XQueryEvaluator ev = load(article);
                ev.setExternalVariable(new QName("want-indexes"), new XdmAtomicValue(true));
                articleIndexes = ev.evaluate();
            } else if (key.equals("meta")) {
                XQueryEvaluator ev = load(index);
                ev.setExternalVariable(new QName("mode"), new XdmAtomicValue("meta"));
                store(run(ev));
            } else if (key.equals("vocab")) {
                XQueryEvaluator ev = load(index);
                ev.setExternalVariable(new QName("mode"), new XdmAtomicValue("vocab"));
                store(run(ev));
            } else if (key.startsWith("part:")) {
                XQueryEvaluator ev = load(index);
                ev.setExternalVariable(new QName("mode"), new XdmAtomicValue("part"));
                ev.setExternalVariable(new QName("group"), new XdmAtomicValue(Long.parseLong(key.substring(5))));
                ev.setExternalVariable(new QName("parts"), new XdmAtomicValue((long) parts));
                ev.setExternalVariable(new QName("heavy"), new XdmAtomicValue(HEAVY));
                store(run(ev));
            } else if (key.equals("global") || key.equals("reader")) {
                XQueryEvaluator ev = load(global);
                ev.setExternalVariable(new QName("i18n"), new XdmAtomicValue(home.resolve("static/i18n.js").toString()));
                ev.setExternalVariable(new QName("ui"), new XdmAtomicValue(home.resolve("static/hwph_ui.html").toString()));
                ev.setExternalVariable(new QName("lang"), new XdmAtomicValue(lang));
                if (key.equals("reader")) ev.setExternalVariable(new QName("only"), new XdmAtomicValue("reader"));
                store(run(ev));
            } else if (key.equals("manifest")) {
                runJob("meta");
                XQueryEvaluator ev = load(manifest);
                ev.setExternalVariable(new QName("site"), new XdmAtomicValue("http://127.0.0.1:" + port + "/"));
                ev.setExternalVariable(new QName("meta-text"), new XdmAtomicValue(read(cache.resolve("data/meta.js"))));
                ev.setExternalVariable(new QName("pdir-text"), new XdmAtomicValue(PDIR));
                ev.setExternalVariable(new QName("katex"), new XdmAtomicValue(home.resolve("static/katex").toUri().toString()));
                write(cache.resolve("manifest.json"), run(ev));
            } else if (key.startsWith("article:")) {
                runArticle(key.substring(8));
            }
        }

        /** an article: its card, its texts and its page, all three from one run */
        void runArticle(String id) throws Exception {
            CompletableFuture<Void> idx = submit("indexes", 0);
            idx.get();
            XQueryEvaluator ev = load(article);
            ev.setExternalVariable(new QName("ids"), new XdmAtomicValue(id));
            ev.setExternalVariable(new QName("indexes"), articleIndexes);
            ev.setExternalVariable(new QName("i18n"), new XdmAtomicValue(home.resolve("static/i18n.js").toString()));
            ev.setExternalVariable(new QName("lang"), new XdmAtomicValue(lang));
            store(run(ev));
        }

        /** makes key now, on the asking thread for an article, through the worker otherwise */
        void ensure(String key) throws Exception {
            if (key.startsWith("article:")) {
                CompletableFuture<Void> mine = new CompletableFuture<>();
                CompletableFuture<Void> f = jobs.putIfAbsent(key, mine);
                if (f == null) {
                    long t = System.currentTimeMillis();
                    try {
                        make(key);
                        mine.complete(null);
                        log(key + " (" + secs(t) + ")");
                    } catch (Throwable e) {
                        mine.completeExceptionally(e);
                        jobs.remove(key, mine);
                        throw e instanceof Exception ? (Exception) e : new RuntimeException(e);
                    }
                    return;
                }
                f.get();
                return;
            }
            submit(key, 0).get();
        }

        XQueryEvaluator load(XQueryExecutable exe) throws SaxonApiException {
            XQueryEvaluator ev = exe.load();
            ev.setContextItem(doc);
            return ev;
        }

        /** the result of a query as one text (its items are strings, written one after the other) */
        String run(XQueryEvaluator ev) throws SaxonApiException {
            StringBuilder sb = new StringBuilder();
            for (XdmItem it : ev.evaluate()) sb.append(it.getStringValue());
            return sb.toString();
        }

        /** writes the files of a query's output: a line "@@FILE@@ <path>" starts each */
        void store(String out) throws IOException {
            int i = out.indexOf("@@FILE@@ ");
            while (i >= 0) {
                int nl = out.indexOf('\n', i);
                String path = out.substring(i + 9, nl).trim();
                int next = out.indexOf("\n@@FILE@@ ", nl);
                String body = out.substring(nl + 1, next < 0 ? out.length() : next + 1);
                write(cache.resolve(path), body);
                i = next < 0 ? -1 : next + 1;
            }
        }

        void close() {
            closed = true;
            worker.interrupt();
        }
    }

    static class Task implements Comparable<Task> {
        static final AtomicLong SEQ = new AtomicLong();
        final String key; final int priority; final long seq = SEQ.incrementAndGet();
        Task(String key, int priority) { this.key = key; this.priority = priority; }
        public int compareTo(Task o) {
            return priority != o.priority ? Integer.compare(priority, o.priority) : Long.compare(seq, o.seq);
        }
    }

    // ------------------------------------------------------------------ which job makes which address
    static final Pattern ARTICLE = Pattern.compile("(?:data/[at]/|pages/)(\\d+)\\.(?:js|html)");
    static final Pattern SHARD = Pattern.compile("data/[sp]/([0-9a-f]+)(?:-[0-9a-f]+)?\\.js");

    String jobFor(String path) {
        Matcher m = ARTICLE.matcher(path);
        if (m.matches()) return "article:" + m.group(1);
        if (path.equals("index.html")) return "reader";
        if (path.equals("data/meta.js")) return "meta";
        if (path.equals("data/vocab.js")) return "vocab";
        if (path.equals("manifest.json")) return "manifest";
        m = SHARD.matcher(path);
        if (m.matches()) return "part:" + (Integer.parseInt(m.group(1), 16) % parts);
        if (path.startsWith("data/") || path.equals("pages/index.html")) return "global";
        return null;
    }

    /** a file of the project that is served as it is */
    Path staticFile(String path) {
        if (path.equals("static_api.js") || path.equals("i18n.js") || path.startsWith("katex/"))
            return home.resolve("static").resolve(path);
        if (path.equals("pages/page.css")) return home.resolve("static/page.css");
        if (path.startsWith("img/") && img != null) return img.resolve(path.substring(4));
        return null;
    }

    // ------------------------------------------------------------------ HTTP
    void handle(HttpExchange ex) throws IOException {
        String path = "";
        try {
            path = URLDecoder.decode(ex.getRequestURI().getRawPath(), "UTF-8");
            if (path.startsWith("/")) path = path.substring(1);
            if (path.isEmpty()) path = "index.html";
            if (path.contains("..") || path.contains("\\")) { send(ex, 400, "text/plain", "bad path".getBytes(StandardCharsets.UTF_8)); return; }
            if (!ex.getRequestMethod().equals("GET") && !ex.getRequestMethod().equals("HEAD")) {
                send(ex, 405, "text/plain", new byte[0]);
                return;
            }
            Path st = staticFile(path);
            if (st != null) {
                if (Files.isRegularFile(st)) send(ex, 200, type(path), Files.readAllBytes(st));
                else send(ex, 404, "text/plain", ("no file: " + path).getBytes(StandardCharsets.UTF_8));
                return;
            }
            if (path.equals("data/pdir.js")) { send(ex, 200, type(path), PDIR.getBytes(StandardCharsets.UTF_8)); return; }
            Generation g = current();
            Path file = g.cache.resolve(path);
            if (!Files.isRegularFile(file)) {
                String job = jobFor(path);
                if (job != null) g.ensure(job);
            }
            if (Files.isRegularFile(file)) send(ex, 200, type(path), Files.readAllBytes(file));
            else send(ex, 404, "text/plain", ("no file: " + path).getBytes(StandardCharsets.UTF_8));
        } catch (Throwable e) {
            Throwable c = e instanceof ExecutionException && e.getCause() != null ? e.getCause() : e;
            log(path + ": " + c);
            send(ex, 500, "text/plain; charset=utf-8", ("error: " + c).getBytes(StandardCharsets.UTF_8));
        }
    }

    static String type(String path) {
        String p = path.toLowerCase(Locale.ROOT);
        if (p.endsWith(".html")) return "text/html; charset=utf-8";
        if (p.endsWith(".js")) return "application/javascript; charset=utf-8";
        if (p.endsWith(".json")) return "application/json; charset=utf-8";
        if (p.endsWith(".css")) return "text/css; charset=utf-8";
        if (p.endsWith(".png")) return "image/png";
        if (p.endsWith(".svg")) return "image/svg+xml";
        if (p.endsWith(".woff2")) return "font/woff2";
        if (p.endsWith(".woff")) return "font/woff";
        if (p.endsWith(".ttf")) return "font/ttf";
        return "application/octet-stream";
    }

    static void send(HttpExchange ex, int code, String type, byte[] body) throws IOException {
        ex.getResponseHeaders().set("Content-Type", type);
        ex.getResponseHeaders().set("Cache-Control", "no-store");
        boolean head = ex.getRequestMethod().equals("HEAD");
        ex.sendResponseHeaders(code, head ? -1 : (body.length == 0 ? -1 : body.length));
        if (!head && body.length > 0) try (OutputStream os = ex.getResponseBody()) { os.write(body); }
        ex.close();
    }

    // ------------------------------------------------------------------ changes
    /** the generation to answer with: a new one when the database, a query or a volume changed */
    Generation current() throws Exception {
        long now = System.currentTimeMillis();
        if (now - lastCheck < 2000 && gen != null) return gen;
        synchronized (reloadLock) {
            lastCheck = System.currentTimeMillis();
            if (src != null && newestVolume() > mtime(db)) {
                log("тома изменились — md2xml.py …");
                long t = System.currentTimeMillis();
                Process p = new ProcessBuilder(python, home.resolve("md2xml.py").toString(), src.toString(), "-o", db.toString())
                        .inheritIO().start();
                if (p.waitFor() != 0) throw new IOException("md2xml.py завершился с ошибкой");
                log("md2xml.py (" + secs(t) + ")");
            }
            long stamp = stamp();
            if (gen == null || gen.stamp != stamp) {
                Generation old = gen;
                if (old != null) { old.close(); log("изменения — читалка собирается заново"); }
                gen = null;
                gen = new Generation(stamp);
                if (old != null) deleteTree(old.cache);
            }
            return gen;
        }
    }

    long stamp() throws IOException {
        long s = mtime(db);
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(home.resolve("xq"), "*.xq")) {
            for (Path p : ds) s = Math.max(s, mtime(p));
        }
        return s;
    }

    long newestVolume() throws IOException {
        long s = 0;
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(src, "{Bd*.md,extras.json}")) {
            for (Path p : ds) s = Math.max(s, mtime(p));
        }
        return s;
    }

    static long mtime(Path p) throws IOException {
        return Files.exists(p) ? Files.getLastModifiedTime(p).toMillis() : 0;
    }

    // ------------------------------------------------------------------ small things
    static void write(Path p, String text) throws IOException {
        Files.createDirectories(p.getParent());
        Path tmp = p.resolveSibling(p.getFileName() + ".tmp" + Thread.currentThread().getId());
        Files.write(tmp, text.getBytes(StandardCharsets.UTF_8));
        Files.move(tmp, p, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
    }

    static String read(Path p) throws IOException {
        return new String(Files.readAllBytes(p), StandardCharsets.UTF_8);
    }

    static void deleteTree(Path root) {
        if (!Files.exists(root)) return;
        try {
            Files.walk(root).sorted(Comparator.reverseOrder()).forEach(p -> p.toFile().delete());
        } catch (IOException ignored) { }
    }

    static final SimpleDateFormat HMS = new SimpleDateFormat("HH:mm:ss");

    static synchronized void log(String s) {
        System.out.println("[" + HMS.format(new Date()) + "] " + s);
    }

    static String secs(long t0) {
        return String.format(Locale.ROOT, "%.1f с", (System.currentTimeMillis() - t0) / 1000.0);
    }

    // ------------------------------------------------------------------ start
    public static void main(String[] args) throws Exception {
        HwphServer s = new HwphServer();
        try {
            s.home = Paths.get(HwphServer.class.getProtectionDomain().getCodeSource().getLocation().toURI()).getParent().getParent();
        } catch (Exception e) {
            s.home = Paths.get(".").toAbsolutePath();
        }
        for (int i = 0; i < args.length; i++) {
            String a = args[i];
            switch (a) {
                case "--db": s.db = Paths.get(args[++i]).toAbsolutePath(); break;
                case "--src": s.src = Paths.get(args[++i]).toAbsolutePath(); break;
                case "--img": s.img = Paths.get(args[++i]).toAbsolutePath(); break;
                case "--port": s.port = Integer.parseInt(args[++i]); break;
                case "--parts": s.parts = Integer.parseInt(args[++i]); break;
                case "--lang": s.lang = args[++i]; break;
                case "--python": s.python = args[++i]; break;
                case "--home": s.home = Paths.get(args[++i]).toAbsolutePath(); break;
                case "--cache": s.cacheRoot = Paths.get(args[++i]).toAbsolutePath(); break;
                case "--open": s.open = true; break;
                default:
                    System.err.println("usage: java -Xmx3g -jar hwph-server.jar --db hwph-data.xml [--src <folder with Bd01.md …>]"
                            + " [--img <folder>] [--port 8000] [--lang ru] [--python python] [--cache <folder>] [--open]");
                    System.exit(2);
            }
        }
        if (s.db == null) { System.err.println("--db is required"); System.exit(2); }
        if (s.img == null && s.src != null) s.img = s.src.resolve("img");
        if (s.cacheRoot == null) s.cacheRoot = s.db.resolveSibling(s.db.getFileName().toString().replaceFirst("\\.xml$", "") + "-cache");
        deleteTree(s.cacheRoot);                 // what an earlier run left
        if (s.src != null && !Files.exists(s.db)) {
            log("базы ещё нет — md2xml.py …");
            Process p = new ProcessBuilder(s.python, s.home.resolve("md2xml.py").toString(), s.src.toString(), "-o", s.db.toString())
                    .inheritIO().start();
            if (p.waitFor() != 0) { System.err.println("md2xml.py завершился с ошибкой"); System.exit(1); }
        }
        s.current();
        HttpServer http = HttpServer.create(new InetSocketAddress("127.0.0.1", s.port), 0);
        http.createContext("/", ex -> s.handle(ex));
        http.setExecutor(Executors.newFixedThreadPool(8));
        http.start();
        String url = "http://127.0.0.1:" + s.port + "/";
        log("читалка: " + url + "  (Ctrl+C — остановить)");
        if (s.open) {
            try { java.awt.Desktop.getDesktop().browse(new URI(url)); } catch (Throwable e) { log("браузер не открылся: " + e); }
        }
    }
}
