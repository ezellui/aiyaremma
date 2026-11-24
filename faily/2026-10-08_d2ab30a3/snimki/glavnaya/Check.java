import java.io.*;
import java.lang.reflect.*;
import java.nio.file.*;
import net.sf.saxon.Configuration;
import net.sf.saxon.query.*;
import net.sf.saxon.s9api.*;

/** Statically compile every .xq main module and every .xsl in a query-configs directory. */
public class Check {
    static Object get(Class<?> c, String f) throws Exception { Field x = c.getDeclaredField(f); x.setAccessible(true); return x.get(null); }
    static void set(Class<?> c, String f, Object v) throws Exception { Field x = c.getDeclaredField(f); x.setAccessible(true); x.set(null, v); }

    public static void main(String[] a) throws Exception {
        String dir = a[0];
        Configuration cfg = xdb.util.XmlUtil.SAXON_CONFIG;
        cfg.setAllowExternalFunctions(true);
        Class<?> qcm = Class.forName("xdb.config.QueryConfigManager");
        set(qcm, "configRoot", dir);
        Class<?> xq = Class.forName("xdb.dom.XQueryEngine");
        int bad = 0;
        File[] files = new File(dir).listFiles();
        java.util.Arrays.sort(files);
        for (File f : files) {
            String name = f.getName();
            String text = new String(Files.readAllBytes(f.toPath()), "UTF-8");
            try {
                if (name.endsWith(".xq")) {
                    if (text.startsWith("module namespace")) {
                        // library module: compile a stub importing it
                        text = "import module namespace c = \"common.xq\" at \"common.xq\"; ()";
                    }
                    StaticQueryContext sqc = new StaticQueryContext(cfg);
                    sqc.setModuleURIResolver((ModuleURIResolver) get(xq, "MR"));
                    sqc.setExternalNamespaceResolver((net.sf.saxon.om.NamespaceResolver) get(xq, "NR"));
                    sqc.compileQuery(text);
                    System.out.println("OK   " + name);
                } else if (name.endsWith(".xsl")) {
                    XsltCompiler comp = xdb.util.XmlUtil.PROCESSOR.newXsltCompiler();
                    comp.compile(new javax.xml.transform.stream.StreamSource(new StringReader(text)));
                    System.out.println("OK   " + name);
                }
            } catch (Throwable t) {
                bad++;
                System.out.println("FAIL " + name + " : " + String.valueOf(t).replace('\n', ' '));
            }
        }
        System.out.println("failures: " + bad);
    }
}
