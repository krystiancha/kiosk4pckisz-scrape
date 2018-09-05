from http.server import HTTPServer, BaseHTTPRequestHandler
from json import dumps

from kiosk4pckisz_scrape.encoders import MovieShowTupleJSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        scraper = MovieShowScraper('http://127.0.0.1:8081', '/filmy,80')
        body = dumps(scraper(), indent=2, sort_keys=True, cls=MovieShowTupleJSONEncoder, ensure_ascii=False)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))


server = HTTPServer(('127.0.0.1', 8000), CustomHTTPRequestHandler)

try:
    server.serve_forever()
except KeyboardInterrupt:
    server.server_close()
