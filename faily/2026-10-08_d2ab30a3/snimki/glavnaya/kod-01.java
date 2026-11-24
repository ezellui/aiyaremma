    private final ServletOutputStream sos = new ServletOutputStream() {

        @Override
        public void write(int b) throws IOException {
            baos.write(b);
        }

        @Override
        public boolean isReady() {
            return true;
        }

        @Override
        public void setWriteListener(javax.servlet.WriteListener writeListener) {
            throw new UnsupportedOperationException("Async I/O is not supported");
        }
    };