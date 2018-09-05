from datetime import timedelta, datetime
from typing import List
from uuid import UUID, uuid4


class MovieStub:
    index: int
    link: str
    title: str
    showtimes: List[datetime]

    def __init__(self, index: int, link: str = None, title='', showtimes=None) -> None:
        if link is None:
            link = ''
        if showtimes is None:
            showtimes = []
        self.index = index
        self.link = link
        self.title = title
        self.showtimes = showtimes

    def __str__(self) -> str:
        return 'index: {}    title: {}    link: {}'.format(self.index or '?', self.title or '?', self.link or '?')


class Movie:
    id: UUID
    title: str
    description: str
    poster: str
    production: str
    genre: str
    duration: timedelta

    def __init__(self, movie_stub: MovieStub) -> None:
        self.id = uuid4()
        self.title = movie_stub.title
        self.description = ''
        self.poster = ''
        self.production = ''
        self.genre = ''
        self.duration = ''


class Show:
    id: UUID
    movie: Movie
    start: datetime
    premiere: bool
    end: datetime

    def __init__(self, movie: Movie, start: datetime, premiere: bool):
        self.id = uuid4()
        self.movie = movie
        self.start = start
        self.premiere = premiere
        self.end = start + movie.duration
