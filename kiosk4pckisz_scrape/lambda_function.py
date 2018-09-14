from json import dumps

from kiosk4pckisz_scrape.caches import MovieShowCache
from kiosk4pckisz_scrape.encoders import JSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper


def lambda_handler(event=None, context=None):
    cache = MovieShowCache(MovieShowScraper())
    movies, shows = cache.get()

    return {
        'statusCode': 200,
        'body': dumps(
            dumps({'movies': sorted(movies, key=lambda o: o.idx), 'shows': sorted(shows, key=lambda o: o.start)},
                  indent=2, cls=JSONEncoder, ensure_ascii=False), cls=JSONEncoder, ensure_ascii=False),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
