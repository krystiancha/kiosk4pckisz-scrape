from datetime import datetime

from boto3 import resource

from kiosk4pckisz_scrape.models import Movie, Show
from kiosk4pckisz_scrape.scrapers import MovieShowScraper


class MovieShowCache:
    scraper: MovieShowScraper

    def __init__(self, scraper: MovieShowScraper) -> None:
        self.scraper = scraper

        self.dynamodb = resource('dynamodb')
        self.meta_table = self.dynamodb.Table('kiosk4pckisz-meta')
        self.movies_table = self.dynamodb.Table('kiosk4pckisz-movies')
        self.shows_table = self.dynamodb.Table('kiosk4pckisz-shows')

    def is_available(self):
        response = self.meta_table.get_item(
            Key={
                'key': 'last_update'
            }
        )

        try:
            last_update = datetime.fromtimestamp(response['Item']['val'])
        except KeyError:
            return False

        if datetime.now().date() > last_update.date():
            return False

        return len(self.movies_table.scan()['Items']) > 0 and len(self.shows_table.scan()['Items']) > 0

    def cache(self):
        movies, shows = self.scraper.scrape()

        with self.movies_table.batch_writer() as batch:
            for movie in self.movies_table.scan()['Items']:
                batch.delete_item(Key={'id': movie['id']})
        with self.movies_table.batch_writer() as batch:
            for movie in movies:
                batch.put_item(Item=movie.to_dict())

        with self.shows_table.batch_writer() as batch:
            for show in self.shows_table.scan()['Items']:
                batch.delete_item(Key={'id': show['id']})
        with self.shows_table.batch_writer() as batch:
            for show in shows:
                # show_dict = show.to_dict()
                # show_dict['movie'] = show_dict['movie']['id']
                batch.put_item(Item=show.to_dict())

        self.meta_table.update_item(
            Key={'key': 'last_update'},
            UpdateExpression='SET val = :val1',
            ExpressionAttributeValues={':val1': int(datetime.now().timestamp())}
        )

        return movies, shows

    def get(self):
        movies = self.movies_table.scan()['Items']
        shows = self.shows_table.scan()['Items']

        if self.is_available() and len(movies) > 0 and len(shows) > 0:
            return list(map(lambda o: Movie.from_dict(o), movies)), list(map(lambda o: Show.from_dict(o), shows))

        return self.cache()
