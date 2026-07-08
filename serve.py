import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Redirect root to index.html
        if self.path == '/' or self.path == '':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"FITAI running at http://localhost:{PORT}")
    print(f"Open: http://localhost:{PORT}")
    httpd.serve_forever()

