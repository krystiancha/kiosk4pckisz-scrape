from json import JSONEncoder, dumps

from kiosk4pckisz_scrape.models import Movie, Show


class CustomJSONEncoder(JSONEncoder):
    classes = []
    attrs_direct = []
    attrs_str = []

    def default(self, o):
        if type(o) in self.classes:
            dict_ = {}
            dict_.update({key: getattr(o, key) for key in self.attrs_direct})
            dict_.update({key: str(getattr(o, key)) for key in self.attrs_str})
            return dict_

        return super().default(o)


class MovieJSONEncoder(CustomJSONEncoder):
    classes = [Movie]
    attrs_direct = ['title', 'description', 'poster', 'production', 'genre']
    attrs_str = ['id', 'duration']


class MovieShowTupleJSONEncoder(MovieJSONEncoder):
    classes = [Movie, Show]

    def default(self, o):
        if type(o) == Movie:
            return MovieJSONEncoder.default(self, o)
        if type(o) == Show:
            return {
                'id': str(o.id),
                'start': str(o.start),
                'end': str(o.end),
                'theater': o.theater,
                'movie': self.default(o.movie)
            }
        return JSONEncoder.default(self, o)
