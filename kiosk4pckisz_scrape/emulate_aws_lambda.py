from http.server import HTTPServer, BaseHTTPRequestHandler
from json import dumps

from kiosk4pckisz_scrape.caches import MovieShowCache
from kiosk4pckisz_scrape.encoders import JSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        cache = MovieShowCache(MovieShowScraper())
        movies, shows = cache.get()
        body = dumps({'movies': sorted(movies, key=lambda o: o.idx), 'shows': sorted(shows, key=lambda o: o.start)}, indent=2, cls=JSONEncoder, ensure_ascii=False).replace(
            'http://127.0.0.1:8081', 'http://pckisz.pl')
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
