import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.webapp.WebAppContext;
import org.eclipse.jetty.webapp.Configuration;

public class Run {
    public static void main(String[] a) throws Exception {
        // Debian's saxonb defaults allowExternalFunctions=false; upstream Maven jar defaults to true
        xdb.util.XmlUtil.SAXON_CONFIG.setAllowExternalFunctions(true);
        Server server = new Server(8080);
        WebAppContext ctx = new WebAppContext();
        ctx.setContextPath("/eldamo");
        ctx.setResourceBase(a[0]);
        ctx.setExtraClasspath(a[1]);
        ctx.setParentLoaderPriority(true);
        ctx.setAttribute("org.eclipse.jetty.server.webapp.ContainerIncludeJarPattern", ".*/tomcat9-.*\\.jar$|.*/jetty9-apache-jsp.*\\.jar$");
        Configuration.ClassList cl = Configuration.ClassList.setServerDefault(server);
        cl.addBefore("org.eclipse.jetty.webapp.JettyWebXmlConfiguration",
            "org.eclipse.jetty.annotations.AnnotationConfiguration");
        server.setHandler(ctx);
        server.start();
        server.join();
    }
}
