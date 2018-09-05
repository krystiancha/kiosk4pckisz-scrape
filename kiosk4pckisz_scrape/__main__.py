from json import dumps

from kiosk4pckisz_scrape.encoders import MovieShowTupleJSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper

scraper = MovieShowScraper('http://127.0.0.1:8081', '/filmy,80')
print(dumps(scraper(), indent=2, sort_keys=True, cls=MovieShowTupleJSONEncoder, ensure_ascii=False))
