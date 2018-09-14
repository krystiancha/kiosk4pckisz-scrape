from json import dumps

from kiosk4pckisz_scrape.caches import MovieShowCache
from kiosk4pckisz_scrape.encoders import JSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper

# scraper = MovieShowScraper('http://127.0.0.1:8081', '/filmy,80')
# print(dumps(scraper.scrape(), indent=2, cls=JSONEncoder, ensure_ascii=False))

cache = MovieShowCache(MovieShowScraper())#'http://127.0.0.1:8081', '/filmy,80'))
data = cache.get()
print(dumps({'movies': data[0], 'shows': data[1]}, indent=2, cls=JSONEncoder, ensure_ascii=False))
