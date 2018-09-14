from datetime import timedelta, datetime
from typing import List, Tuple
from uuid import UUID, uuid4


class MovieStub:
    index: int
    link: str
    original_title: str
    title: str
    showtimes: List[Tuple[datetime, int]]

    def __init__(self, index: int, link: str = '', original_title: str = '', title: str = '', showtimes=None) -> None:
        if showtimes is None:
            showtimes = []

        self.index = index
        self.link = link
        self.original_title = original_title
        self.title = title
        self.showtimes = showtimes

    def __str__(self) -> str:
        ret = "#{} ".format(self.index + 1)
        if self.title:
            ret += "{} ".format(self.title)
        if self.link:
            ret += "{}  ".format(self.link)

        return ret

    def __eq__(self, o: object) -> bool:
        if type(o) == MovieStub:
            return self.title == o.title
        return super().__eq__(o)


class Movie:
    id: UUID
    link: str
    title: str
    description: str
    poster: str
    production: str
    genre: str
    duration: timedelta

    def __init__(self, movie_stub: MovieStub) -> None:
        self.id = uuid4()
        self.link = movie_stub.link
        self.title = movie_stub.title
        self.description = ''
        self.poster = ''
        self.production = ''
        self.genre = ''
        self.duration = timedelta()

    def __str__(self) -> str:
        ret = ""
        if self.title:
            ret += "{} ".format(self.title)
        if self.link:
            ret += "{} ".format(self.link)

        return ret


class Show:
    id: UUID
    movie: Movie
    start: datetime
    premiere: bool
    end: datetime
    theater: int

    def __init__(self, movie: Movie, start: datetime, premiere: bool, theater: int):
        self.id = uuid4()
        self.movie = movie
        self.start = start
        self.premiere = premiere
        self.end = start + movie.duration
        self.theater = theater
