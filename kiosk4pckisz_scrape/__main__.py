from json import dumps

from kiosk4pckisz_scrape.caches import MovieShowCache
from kiosk4pckisz_scrape.encoders import JSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper

# scraper = MovieShowScraper('http://127.0.0.1:8081', '/filmy,80')
# print(dumps(scraper.scrape(), indent=2, cls=JSONEncoder, ensure_ascii=False))

cache = MovieShowCache(MovieShowScraper())#'http://127.0.0.1:8081', '/filmy,80'))
movies, shows = cache.get()
print(dumps({'movies': sorted(movies, key=lambda o: o.idx), 'shows': sorted(shows, key=lambda o: o.start)}, indent=2, cls=JSONEncoder, ensure_ascii=False).replace(
    'http://127.0.0.1:8081', 'http://pckisz.pl'))
