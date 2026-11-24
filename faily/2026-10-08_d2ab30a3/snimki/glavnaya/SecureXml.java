package xdb.util;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.SAXParserFactory;

/**
 * Factories for XML parsers that refuse DOCTYPE declarations, external entities and external DTDs
 * (XXE). Eldamo data and configuration files use none of these features.
 */
public final class SecureXml {

    private static final String DISALLOW_DOCTYPE = "http://apache.org/xml/features/disallow-doctype-decl";
    private static final String EXTERNAL_GENERAL = "http://xml.org/sax/features/external-general-entities";
    private static final String EXTERNAL_PARAMETER = "http://xml.org/sax/features/external-parameter-entities";
    private static final String LOAD_EXTERNAL_DTD = "http://apache.org/xml/features/nonvalidating/load-external-dtd";

    private SecureXml() {
    }

    /**
     * A non-validating, non-namespace-aware SAX parser factory hardened against XXE.
     *
     * @return The factory.
     */
    public static SAXParserFactory newSaxParserFactory() {
        SAXParserFactory factory = SAXParserFactory.newInstance();
        factory.setValidating(false);
        factory.setNamespaceAware(false);
        factory.setXIncludeAware(false);
        setFeature(factory, XMLConstants.FEATURE_SECURE_PROCESSING, true);
        setFeature(factory, DISALLOW_DOCTYPE, true);
        setFeature(factory, EXTERNAL_GENERAL, false);
        setFeature(factory, EXTERNAL_PARAMETER, false);
        setFeature(factory, LOAD_EXTERNAL_DTD, false);
        return factory;
    }

    /**
     * A DOM builder factory hardened against XXE.
     *
     * @return The factory.
     */
    public static DocumentBuilderFactory newDocumentBuilderFactory() {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setXIncludeAware(false);
        factory.setExpandEntityReferences(false);
        setFeature(factory, XMLConstants.FEATURE_SECURE_PROCESSING, true);
        setFeature(factory, DISALLOW_DOCTYPE, true);
        setFeature(factory, EXTERNAL_GENERAL, false);
        setFeature(factory, EXTERNAL_PARAMETER, false);
        setFeature(factory, LOAD_EXTERNAL_DTD, false);
        return factory;
    }

    private static void setFeature(SAXParserFactory factory, String feature, boolean value) {
        try {
            factory.setFeature(feature, value);
        } catch (Exception ex) {
            // Feature not supported by this parser implementation; the remaining ones still apply.
        }
    }

    private static void setFeature(DocumentBuilderFactory factory, String feature, boolean value) {
        try {
            factory.setFeature(feature, value);
        } catch (Exception ex) {
            // Feature not supported by this parser implementation; the remaining ones still apply.
        }
    }
}
