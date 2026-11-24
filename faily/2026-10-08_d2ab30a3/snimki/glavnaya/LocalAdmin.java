package xdb.control;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * Guard for administrative pages that rewrite the data file (merge.jsp, accept-refs.jsp). They are
 * only allowed as POST requests coming from the local machine, so that visiting a link or an image
 * URL, or a request from another host, cannot modify the data.
 */
public final class LocalAdmin {

    private LocalAdmin() {
    }

    /**
     * Check that the request is a POST from a loopback address. If it is not, an error response is
     * sent and false is returned.
     *
     * @param request
     *            The request.
     * @param response
     *            The response.
     * @return True if the action may proceed.
     * @throws IOException
     *             For errors writing the error response.
     */
    public static boolean allow(HttpServletRequest request, HttpServletResponse response)
        throws IOException {
        if (!isLoopback(request.getRemoteAddr())) {
            response.sendError(HttpServletResponse.SC_FORBIDDEN, "Only allowed from the local machine");
            return false;
        }
        if (!"POST".equals(request.getMethod())) {
            response.setHeader("Allow", "POST");
            response.sendError(HttpServletResponse.SC_METHOD_NOT_ALLOWED, "Use POST");
            return false;
        }
        return true;
    }

    /**
     * URL of a page of this web application, addressed through the loopback interface rather than
     * the Host header supplied by the client.
     *
     * @param request
     *            The request.
     * @param path
     *            The path inside the web application, starting with "/".
     * @return The URL.
     */
    public static String localUrl(HttpServletRequest request, String path) {
        return "http://127.0.0.1:" + request.getLocalPort() + request.getContextPath() + path;
    }

    static boolean isLoopback(String address) {
        if (address == null) {
            return false;
        }
        try {
            return InetAddress.getByName(address).isLoopbackAddress();
        } catch (UnknownHostException ex) {
            return false;
        }
    }
}
