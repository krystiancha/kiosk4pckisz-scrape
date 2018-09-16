from datetime import datetime

from boto3 import resource

from kiosk4pckisz_scrape.scrapers import MovieShowScraper


def lambda_handler(event=None, context=None):
    scraper = MovieShowScraper()
    movies, shows = scraper.scrape()

    dynamodb = resource('dynamodb')
    meta_table = dynamodb.Table('kiosk4pckisz-meta')
    movies_table = dynamodb.Table('kiosk4pckisz-movies')
    shows_table = dynamodb.Table('kiosk4pckisz-shows')

    with movies_table.batch_writer() as batch:
        for movie in movies_table.scan()['Items']:
            batch.delete_item(Key={'id': movie['id']})
    with movies_table.batch_writer() as batch:
        for movie in movies:
            batch.put_item(Item=movie.to_dict())

    with shows_table.batch_writer() as batch:
        for show in shows_table.scan()['Items']:
            batch.delete_item(Key={'id': show['id']})
    with shows_table.batch_writer() as batch:
        for show in shows:
            batch.put_item(Item=show.to_dict())

    meta_table.update_item(
        Key={'key': 'last_update'},
        UpdateExpression='SET val = :val1',
        ExpressionAttributeValues={':val1': int(datetime.now().timestamp())}
    )

    return {
        'statusCode': 200,
        'body': '',
    }
