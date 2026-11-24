import java.io.File;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import javax.xml.transform.OutputKeys;
import javax.xml.transform.stream.StreamResult;

import net.sf.saxon.Configuration;
import net.sf.saxon.query.DynamicQueryContext;
import net.sf.saxon.query.ModuleURIResolver;
import net.sf.saxon.query.StaticQueryContext;
import net.sf.saxon.query.XQueryExpression;

/**
 * Render one XQuery for many parameter values, the way the Controller does.
 *
 * usage: Render WEBROOT QUERY_FILE PARAM VALUES_FILE OUT_DIR PUBMODE UI_LANG THREADS [check]
 * With "check" as last argument only compiles every .xq in the query-configs directory.
 */
public class Render {
    static void set(Class<?> c, String f, Object v) throws Exception {
        Field x = c.getDeclaredField(f); x.setAccessible(true); x.set(null, v);
    }
    static Object get(Class<?> c, String f) throws Exception {
        Field x = c.getDeclaredField(f); x.setAccessible(true); return x.get(null);
    }
    static Object call(Class<?> c, String m) throws Exception {
        Method x = c.getDeclaredMethod(m); x.setAccessible(true); return x.invoke(null);
    }

    static StaticQueryContext staticContext(Configuration cfg) throws Exception {
        StaticQueryContext sqc = new StaticQueryContext(cfg);
        Class<?> xq = Class.forName("xdb.dom.XQueryEngine");
        sqc.setModuleURIResolver((ModuleURIResolver) get(xq, "MR"));
        sqc.setExternalNamespaceResolver((net.sf.saxon.om.NamespaceResolver) get(xq, "NR"));
        return sqc;
    }

    public static void main(String[] a) throws Exception {
        final Configuration cfg = xdb.util.XmlUtil.SAXON_CONFIG;
        cfg.setAllowExternalFunctions(true);
        String web = a[0];
        Class<?> qcm = Class.forName("xdb.config.QueryConfigManager");
        set(qcm, "configRoot", web + "/config/query-configs");

        if (a.length > 8 && a[8].equals("check")) {
            int bad = 0;
            for (File f : new File(web + "/config/query-configs").listFiles()) {
                if (!f.getName().endsWith(".xq")) continue;
                String text = new String(Files.readAllBytes(f.toPath()), "UTF-8");
                if (text.startsWith("module namespace")) {
                    text = "import module namespace c = \"common.xq\" at \"common.xq\"; ()";
                }
                try {
                    staticContext(cfg).compileQuery(text);
                } catch (Exception e) {
                    bad++;
                    System.out.println("FAIL " + f.getName() + ": " + String.valueOf(e).replace('\n', ' '));
                }
            }
            System.out.println("compile failures: " + bad);
            return;
        }

        Class<?> mcm = Class.forName("xdb.config.ModelConfigManager");
        set(mcm, "configRoot", new File(web + "/config/model-configs"));
        set(mcm, "singleton", call(mcm, "loadData"));
        Class<?> dm = Class.forName("xdb.dom.DomManager");
        set(dm, "dataRoot", web + "/data");
        final Object doc = dm.getMethod("getDoc").invoke(null);

        final XQueryExpression exp = staticContext(cfg).compileQuery(
            new String(Files.readAllBytes(Paths.get(a[1])), "UTF-8"));
        final String param = a[2];
        List<String> values = Files.readAllLines(Paths.get(a[3]));
        final String out = a[4];
        final String pub = a[5];
        final String lang = a[6];
        File catalog = new File(web + "/config/messages/messages-" + lang + ".xml");
        final String messages = (!lang.equals("en") && catalog.isFile()) ? catalog.toURI().toString() : "";
        new File(out).mkdirs();
        final PrintWriter err = new PrintWriter(new java.io.FileWriter(out + "/errors.txt"));
        ExecutorService ex = Executors.newFixedThreadPool(Integer.parseInt(a[7]));
        for (final String value : values) {
            if (value.trim().isEmpty()) continue;
            ex.submit(() -> {
                try {
                    DynamicQueryContext q = new DynamicQueryContext(cfg);
                    q.setParameter(param, value);
                    q.setParameter("pubmode", pub);
                    q.setParameter("{common.xq}ui-lang", lang);
                    q.setParameter("{common.xq}ui-messages", messages);
                    q.setContextItem((net.sf.saxon.om.NodeInfo) doc);
                    Properties p = new Properties();
                    p.setProperty(OutputKeys.METHOD, "html");
                    p.setProperty(OutputKeys.INDENT, "yes");
                    StringWriter sw = new StringWriter();
                    exp.run(q, new StreamResult(sw), p);
                    Files.write(Paths.get(out + "/" + value.replaceAll("[^A-Za-z0-9_-]", "_") + ".html"),
                        sw.toString().getBytes("UTF-8"));
                } catch (Throwable t) {
                    synchronized (err) {
                        err.println(value + "\t" + String.valueOf(t).replace('\n', ' '));
                        err.flush();
                    }
                }
            });
        }
        ex.shutdown();
        ex.awaitTermination(10, TimeUnit.HOURS);
        err.close();
    }
}
