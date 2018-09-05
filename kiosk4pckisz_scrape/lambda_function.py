from json import dumps

from kiosk4pckisz_scrape.encoders import MovieShowTupleJSONEncoder
from kiosk4pckisz_scrape.scrapers import MovieShowScraper


def lambda_handler(event=None, context=None):
    scraper = MovieShowScraper()

    return {
        'statusCode': 200,
        'body': dumps(scraper(), indent=2, sort_keys=True, cls=MovieShowTupleJSONEncoder, ensure_ascii=False),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
