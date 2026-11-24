package xdb.control;

/**
 * The request URI does not correspond to any page; reported to the client as 404.
 */
public class NotFoundException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    /**
     * Constructor.
     *
     * @param message
     *            The message.
     */
    public NotFoundException(String message) {
        super(message);
    }
}
