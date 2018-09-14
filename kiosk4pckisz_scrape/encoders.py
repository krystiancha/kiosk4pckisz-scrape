import json

from kiosk4pckisz_scrape.models import Movie, Show


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) == Movie or type(o) == Show:
            return o.to_dict()
        return super().default(o)
