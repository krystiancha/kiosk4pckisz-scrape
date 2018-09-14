from datetime import timedelta, datetime
from typing import List, Tuple


class MovieStub:
    idx: int
    link: str
    original_title: str
    title: str
    showtimes: List[Tuple[datetime, int]]

    def __init__(self, idx: int, link: str = '', original_title: str = '', title: str = '', showtimes=None) -> None:
        if showtimes is None:
            showtimes = []

        self.idx = idx
        self.link = link
        self.original_title = original_title
        self.title = title
        self.showtimes = showtimes

    def __str__(self) -> str:
        ret = "#{} ".format(self.idx + 1)
        if self.title:
            ret += "{} ".format(self.title)
        if self.link:
            ret += "{}  ".format(self.link)

        return ret

    def __eq__(self, o) -> bool:
        if type(o) == MovieStub:
            return self.title == o.title
        return super().__eq__(o)


class Movie:
    idx: int
    title: str
    description: str
    poster: str
    production: str
    genre: str
    duration: timedelta

    def __init__(self, idx: int, title: str = '', description: str = '', poster: str = '', production: str = '',
                 genre: str = '', duration: timedelta = timedelta()) -> None:
        self.idx = int(idx)
        self.title = title
        self.description = description
        self.poster = poster
        self.production = production
        self.genre = genre
        self.duration = duration

    def __str__(self) -> str:
        return self.title

    def to_dict(self):
        return {
            'id': self.idx,
            'title': self.title,
            'description': self.description,
            'poster': self.poster,
            'production': self.production,
            'genre': self.genre,
            'duration': str(self.duration),
        }

    @staticmethod
    def from_dict(o: dict):
        return Movie(
            idx=o.get('id', 0),
            title=o.get('title', ''),
            description=o.get('description', ''),
            poster=o.get('poster', ''),
            production=o.get('production', ''),
            genre=o.get('genre', ''),
        )

    @staticmethod
    def from_stub(o: MovieStub):
        return Movie(
            idx=o.idx,
            title=o.title,
        )


class Show:
    idx: int
    movie: Movie
    start: datetime
    end: datetime
    theater: int
    premiere: bool

    def __init__(self, idx: int = 0, movie: Movie = None, start: datetime = None, theater: int = 0,
                 premiere: bool = False):
        self.idx = int(idx)
        self.movie = movie
        self.start = start
        self.end = start + movie.duration
        self.theater = int(theater)
        self.premiere = bool(premiere)

    def to_dict(self):
        return {
            'id': self.idx,
            'movie': self.movie.to_dict(),
            'start': self.start.strftime("%Y-%m-%d %H:%M:%S"),
            'end': self.end.strftime("%Y-%m-%d %H:%M:%S"),
            'theater': self.theater,
            'premiere': False,
        }

    @staticmethod
    def from_dict(o: dict):
        return Show(
            idx=o['id'],
            movie=Movie.from_dict(o['movie']),
            start=datetime.strptime(o['start'], "%Y-%m-%d %H:%M:%S"),
            theater=o['theater'],
            premiere=o['premiere'],
        )
