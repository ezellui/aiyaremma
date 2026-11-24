package xdb.l10n;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamReader;

/** Small XML helpers: a safe streaming reader and a deterministic, indented writer. */
final class XmlIO {

    private XmlIO() {
    }

    /** A streaming reader with DTDs and external entities disabled. */
    static XMLStreamReader reader(InputStream in) throws XMLStreamException {
        XMLInputFactory factory = XMLInputFactory.newInstance();
        factory.setProperty(XMLInputFactory.SUPPORT_DTD, false);
        factory.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
        factory.setProperty(XMLInputFactory.IS_COALESCING, true);
        return factory.createXMLStreamReader(in, "UTF-8");
    }

    static InputStream open(File file) throws IOException {
        return new FileInputStream(file);
    }

    /** Attributes of the current start element. */
    static Map<String, String> attributes(XMLStreamReader r) {
        Map<String, String> map = new LinkedHashMap<String, String>();
        for (int i = 0; i < r.getAttributeCount(); i++) {
            map.put(r.getAttributeLocalName(i), r.getAttributeValue(i));
        }
        return map;
    }

    /** Text content of the current element; the reader is left on its end tag. */
    static String text(XMLStreamReader r) throws XMLStreamException {
        StringBuilder sb = new StringBuilder();
        int depth = 1;
        while (depth > 0) {
            int event = r.next();
            if (event == XMLStreamConstants.START_ELEMENT) {
                depth++;
            } else if (event == XMLStreamConstants.END_ELEMENT) {
                depth--;
            } else if (depth == 1 && (event == XMLStreamConstants.CHARACTERS
                || event == XMLStreamConstants.CDATA || event == XMLStreamConstants.SPACE)) {
                sb.append(r.getText());
            }
        }
        return sb.toString();
    }

    /** A UTF-8 writer to a temporary file, renamed over the target when closed. */
    static final class Out implements AutoCloseable {
        private final File target;
        private final File temp;
        final Writer w;

        Out(File target) throws IOException {
            this.target = target;
            File dir = target.getAbsoluteFile().getParentFile();
            if (dir != null) {
                dir.mkdirs();
            }
            this.temp = new File(target.getPath() + ".tmp");
            this.w = new OutputStreamWriter(new BufferedOutputStream(new FileOutputStream(temp)),
                StandardCharsets.UTF_8);
            w.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        }

        void raw(String s) throws IOException {
            w.write(s);
        }

        @Override
        public void close() throws IOException {
            w.close();
            if (target.exists() && !target.delete()) {
                throw new IOException("Cannot replace " + target);
            }
            if (!temp.renameTo(target)) {
                throw new IOException("Cannot rename " + temp + " to " + target);
            }
        }
    }

    static String attr(String name, String value) {
        if (value == null) {
            return "";
        }
        return " " + name + "=\"" + escAttr(value) + "\"";
    }

    static String escAttr(String s) {
        StringBuilder sb = new StringBuilder(s.length() + 8);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '&': sb.append("&amp;"); break;
                case '<': sb.append("&lt;"); break;
                case '>': sb.append("&gt;"); break;
                case '"': sb.append("&quot;"); break;
                case '\n': sb.append("&#10;"); break;
                case '\r': sb.append("&#13;"); break;
                case '\t': sb.append("&#9;"); break;
                default: sb.append(c);
            }
        }
        return sb.toString();
    }

    static String escText(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }

    /** A CDATA section (split where the text contains "]]>"). */
    static String cdata(String s) {
        return "<![CDATA[" + s.replace("]]>", "]]]]><![CDATA[>") + "]]>";
    }
}
