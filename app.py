import json
import pathlib
from urllib.parse import urlparse, unquote_plus
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = pathlib.Path()


class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urlparse(self.path)
        match route.path:
            case "/":
                self.send_html('index.html')
            case "/message":
                self.send_html('message.html')
            case _:
                file = BASE_DIR / route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', 404)

    def do_POST(self):
        raw_data = self.rfile.read(int(self.headers['Content-Length']))
# "вказуємо ліміт потоку для зчитування"
        body = unquote_plus(raw_data.decode())
        body = self.parse_form_data(body)
        print(body)
        path_js = BASE_DIR.joinpath('storage/data.json')
        print(path_js)
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(body, fd, ensure_ascii=False)
# for Wind: encoding='utf-8' - Wind use other coding
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def parse_form_data(self, data):
        raw_params = data.split('&')
        data = {key: value for key, value in [param.split('=') for param in raw_params]}
        return data

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self, filename):
        self.send_response(200)
        mt, *rest = mimetypes.guess_type(filename)
        if mt:
            self.send_header('Content-Type', mt)
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())


def run(server=HTTPServer, handler=HTTPHandler):
    address = ('', 3000)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == '__main__':
    run()
