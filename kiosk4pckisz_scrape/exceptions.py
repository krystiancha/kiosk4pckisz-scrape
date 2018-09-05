from kiosk4pckisz_scrape.models import MovieStub


class ScrapingException(Exception):
    error_code: int
    movie_stub: MovieStub

    class ErrorCode:
        NO_BOX_G_PAGE = 1
        NO_ROW = 2
        NO_A_TAGS = 3
        NO_DIV = 4
        NO_H3 = 5
        NO_H3_TEXT = 6
        NO_SHOWS_SPAN = 7
        DATE_SPLIT_FAILED = 8
        TIMES_SPLIT_FAILED = 9
        CANT_INTERPRET_TIME = 10
        NO_LINK = 11
        NO_IMG = 12
        NO_DETAILS = 13

    def __init__(self, error_code: int, movie_stub: MovieStub = None) -> None:
        self.error_code = error_code
        self.movie_stub = movie_stub

    def __str__(self):
        return '({}, {})'.format(self.error_code, str(self.movie_stub))


class NoFutureShows(Exception):
    pass
