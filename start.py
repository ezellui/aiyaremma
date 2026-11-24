"""Открывает распакованный архив Claude в браузере через localhost."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Timer
from urllib.parse import urlsplit
import webbrowser


class ArchiveHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        path = urlsplit(self.path).path
        if path.startswith('/faily/'):
            self.send_header('Content-Security-Policy', "sandbox; default-src 'none'")
            self.send_header('X-Content-Type-Options', 'nosniff')
        elif path == '/' or path.endswith(('.html','.js','.css')):
            self.send_header('Cache-Control', 'no-cache')
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=3000)
    parser.add_argument('--no-browser', action='store_true', help='Только запустить сервер')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if not (root / 'index.html').is_file():
        parser.error('Распакуйте архив целиком и запустите start.py из него.')
    if not 0 <= args.port <= 65535:
        parser.error('Номер порта должен быть от 0 до 65535.')
    handler = partial(ArchiveHandler, directory=str(root))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError as exc:
        # The default port can already be in use by another local app.
        if args.port != 3000:
            parser.error(str(exc))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    with server:
        url = f'http://127.0.0.1:{server.server_port}/'
        print(f'Архив Claude: {url}\nЧтобы остановить сервер, нажмите Ctrl+C.', flush=True)
        if not args.no_browser:
            browser = Timer(0.15, webbrowser.open, (url,))
            browser.daemon = True
            browser.start()
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
