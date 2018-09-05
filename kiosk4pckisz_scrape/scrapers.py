from datetime import datetime, timedelta
from sys import stderr
from time import mktime, strptime
from typing import List

from bs4 import BeautifulSoup
from requests import get

from kiosk4pckisz_scrape.exceptions import ScrapingException, NoFutureShows
from kiosk4pckisz_scrape.models import MovieStub, Movie, Show


class MovieShowScraper:
    base_url: str
    movie_list_path: str

    def __init__(self, base_url: str = 'http://pckisz.pl', movie_list_path: str = '/filmy,80') -> None:
        self.base_url = base_url
        self.movie_list_path = movie_list_path

    def __call__(self):
        movies: List[Movie] = []
        shows: List[Show] = []
        for stub in self.movie_stubs(self.movie_list_source()):
            try:
                movie = self.movie_from_movie_stub(stub, self.movie_detail_source(stub))
                movies.append(movie)

                movie_shows = map(lambda showtime: Show(movie, showtime, False), stub.showtimes)
                shows += movie_shows
            except ScrapingException as e:
                print(e)

        return {
            'movies': movies,
            'shows': shows,
        }

    def movie_list_source(self) -> str:
        r = get(self.base_url + self.movie_list_path)
        return r.content

    def movie_stubs(self, source):
        soup = BeautifulSoup(source, 'html.parser')

        box_g_page = soup.find(class_='box-g-page')
        if not box_g_page:
            raise ScrapingException(ScrapingException.ErrorCode.NO_BOX_G_PAGE)
        movie_list = box_g_page.find(class_='row')
        if not movie_list:
            raise ScrapingException(ScrapingException.ErrorCode.NO_ROW)
        a_tags = movie_list.find_all('a', recursive=False)
        if not a_tags:
            raise ScrapingException(ScrapingException.ErrorCode.NO_A_TAGS)

        movie_stubs: List[MovieStub] = []
        for idx, a_tag in enumerate(a_tags):
            try:
                movie_stubs.append(self.movie_stub_from_list(a_tag, idx))
            except NoFutureShows:
                break
            except ScrapingException as e:
                print(
                    'ScrapingException: movie {}: error_code {}'.format(e.movie_stub, str(e.error_code)),
                    file=stderr,
                )

        return movie_stubs

    @staticmethod
    def movie_stub_from_list(a_tag, idx, scrape_all=False   ) -> MovieStub:
        movie_stub = MovieStub(idx, a_tag.get('href'))

        if not movie_stub.link:
            raise ScrapingException(ScrapingException.ErrorCode.NO_LINK, movie_stub)

        details_div = a_tag.find('div')
        if not details_div:
            raise ScrapingException(ScrapingException.ErrorCode.NO_DIV, movie_stub)

        title_h3 = details_div.find('h3')
        if not title_h3:
            raise ScrapingException(ScrapingException.ErrorCode.NO_H3, movie_stub)
        if not title_h3.text:
            raise ScrapingException(ScrapingException.ErrorCode.NO_H3_TEXT, movie_stub)
        movie_stub.title = title_h3.text

        shows_span = details_div.find('span', class_='date')
        if not shows_span:
            raise ScrapingException(ScrapingException.ErrorCode.NO_SHOWS_SPAN, movie_stub)
        showdays_raw = shows_span.text.split('  |  ')
        if showdays_raw == shows_span.text:
            raise ScrapingException(ScrapingException.ErrorCode.DATE_SPLIT_FAILED, movie_stub)
        if showdays_raw[-1] == '':
            showdays_raw.pop(-1)

        for showday_raw in showdays_raw:
            try:
                date_raw, showtimes_raw = showday_raw.split(' - ')
            except ValueError:
                raise ScrapingException(ScrapingException.ErrorCode.TIMES_SPLIT_FAILED, movie_stub)
            for showtime_raw in showtimes_raw.split(', '):
                try:
                    showtime = datetime.fromtimestamp(
                        mktime(strptime('{} {}'.format(date_raw, showtime_raw), '%Y.%m.%d %H:%M')))
                except (OverflowError, ValueError):
                    raise ScrapingException(ScrapingException.ErrorCode.CANT_INTERPRET_TIME, movie_stub)
                if showtime > datetime.now() or scrape_all:
                    movie_stub.showtimes.append(showtime)
        if not movie_stub.showtimes and not scrape_all:
            raise NoFutureShows

        return movie_stub

    def movie_detail_source(self, movie_stub):
        r = get(self.base_url + movie_stub.link)
        return r.content

    def movie_from_movie_stub(self, movie_stub, source) -> Movie:
        soup = BeautifulSoup(source, 'html.parser')

        movie = Movie(movie_stub)

        box_g_page = soup.find(class_='box-g-page')
        if not box_g_page:
            raise ScrapingException(ScrapingException.ErrorCode.NO_BOX_G_PAGE, movie_stub)

        img = box_g_page.find('img')
        if not img:
            raise ScrapingException(ScrapingException.ErrorCode.NO_IMG, movie_stub)
        movie.poster = self.base_url + img.get('src') if img.get('src') else ''

        details = box_g_page.find(
            'span',
            style='display:block; position:relative; padding-left:18px; line-height:145%;',
        )

        if not details:
            raise ScrapingException(ScrapingException.ErrorCode.NO_DETAILS, movie_stub)

        movie.description = ''.join(map(lambda p_tag: p_tag.text, box_g_page.find_all('p'))).strip()

        movie.production = self.find_between(details.text, 'Produkcja:', '\r\n\t').strip()

        movie.genre = self.find_between(details.text, 'Gatunek:', ', Czas').strip()

        movie.duration = timedelta(minutes=float(self.find_between(details.text, 'Czas:', 'min').strip()))

        return movie

    @staticmethod
    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ''
