from datetime import datetime, timedelta
from logging import Logger
from re import search, I
from sys import stderr
from time import mktime, strptime
from typing import List

from bs4 import BeautifulSoup
from requests import get

from kiosk4pckisz_scrape.exceptions import MovieListScrapingException
from kiosk4pckisz_scrape.models import MovieStub, Movie, Show


class MovieShowScraper:
    logger: Logger
    base_url: str
    movie_list_path: str

    def __init__(self, logger: Logger, base_url: str = 'http://pckisz.pl', movie_list_path: str = '/filmy,80') -> None:
        self.logger = logger
        self.base_url = base_url
        self.movie_list_path = movie_list_path

    def __call__(self):
        return self.scrape()

    def scrape(self):
        movies: List[Movie] = []
        shows: List[Show] = []

        stubs = self.merge_stubs(self.movie_stubs(self.movie_list_source()))
        stubs_with_shows = filter(lambda o: o.showtimes, stubs)

        for idx, stub in enumerate(stubs_with_shows):
            movie = self.movie_from_movie_stub(stub, self.movie_detail_source(stub))
            movie.idx = idx
            movies.append(movie)

            def stub_show_to_show(stub_show):
                start, theater = stub_show
                return Show(movie=movie, start=start, theater=theater)

            shows += map(stub_show_to_show, stub.showtimes)

        for idx, show in enumerate(shows):
            show.idx = idx

        return movies, shows

    def movie_list_source(self) -> str:
        r = get(self.base_url + self.movie_list_path)
        return r.content

    def movie_stubs(self, source):
        soup = BeautifulSoup(source, 'html.parser')

        box_g_page = soup.find(class_='box-g-page')
        if not box_g_page:
            raise MovieListScrapingException('Element ".box-g-page" not found')
        movie_list = box_g_page.find(class_='row')
        if not movie_list:
            raise MovieListScrapingException('Element ".box-g-page .row" not found')

        movie_stubs: List[MovieStub] = []
        a_tags = enumerate(movie_list.find_all('a', recursive=False))
        if not a_tags:
            raise MovieListScrapingException('No movies found')
        for idx, a_tag in a_tags:
            movie_stubs.append(self.movie_stub_from_list(a_tag, idx))

        return movie_stubs

    @staticmethod
    def merge_stubs(movie_stub: List[MovieStub]):
        merged: List[MovieStub] = []
        for stub in movie_stub:
            try:
                idx = merged.index(stub)
                merged[idx].showtimes += stub.showtimes
            except ValueError:
                merged.append(stub)

        return merged

    @staticmethod
    def parse_title(title):
        match = search(' *-? *(poranek)? *,? *ma[łl]e kino( *- *)?', title, I)
        if match:
            return title[:match.start()] + title[match.end():], 1
        return title, 0

    def movie_stub_from_list(self, a_tag, idx, scrape_all=False) -> MovieStub:
        movie_stub = MovieStub(idx=idx, link=a_tag.get('href'))

        def print_warning(msg):
            self.logger.warning('{} @ movie list: {}'.format(movie_stub, msg))

        details_div = a_tag.find('div')
        if not details_div:
            print_warning("\"div\" not found")
            return movie_stub

        title_h3 = details_div.find('h3')
        theater = 0
        if title_h3:
            if title_h3.text:
                movie_stub.title, theater = MovieShowScraper.parse_title(title_h3.text)
            else:
                print_warning("empty title")
        else:
            print_warning("\"div h3 \" not found")

        shows_span = details_div.find('span', class_='date')
        if shows_span:
            showdays_raw = shows_span.text.split('  |  ')
            if showdays_raw != shows_span.text:
                if showdays_raw[-1] == '':
                    showdays_raw.pop(-1)
                if not showdays_raw:
                    print_warning("movie has no shows")
                for showday_raw in showdays_raw:
                    try:
                        date_raw, showtimes_raw = showday_raw.split(' - ')
                    except ValueError:
                        print_warning("can't split \"{}\" to date and times".format(showday_raw))
                        continue
                    for showtime_raw in showtimes_raw.split(', '):
                        try:
                            showtime = datetime.fromtimestamp(
                                mktime(strptime('{} {}'.format(date_raw, showtime_raw), '%Y.%m.%d %H:%M')))
                        except (OverflowError, ValueError):
                            print_warning("can't interpret date: \"{}\"".format('{} {}'.format(date_raw, showtime_raw)))
                            continue
                        if showtime > datetime.now() or scrape_all:
                            movie_stub.showtimes.append((showtime, theater))
            else:
                print_warning("failed to split string to showdays")
        else:
            print_warning("\"span.date\" not found")

        return movie_stub

    def movie_detail_source(self, movie_stub):
        r = get(self.base_url + movie_stub.link)
        return r.content

    def movie_from_movie_stub(self, stub, source) -> Movie:
        movie = Movie.from_stub(stub)

        def print_warning(msg):
            self.logger.warning('{} @ movie detail: {}'.format(movie, msg))

        soup = BeautifulSoup(source, 'html.parser')

        box_g_page = soup.find(class_='box-g-page')
        if not box_g_page:
            print_warning("Element \".box-g-page\" not found")
            return movie

        img = box_g_page.find('img')
        if not img:
            print_warning("Element \".box-g-page img\" not found")
            return movie

        if img.get('src'):
            movie.poster = self.base_url + img.get('src')
        else:
            print_warning("movie has no poster")

        details = box_g_page.find(
            'span',
            style='display:block; position:relative; padding-left:18px; line-height:145%;',
        )
        if not details:
            print_warning("Element \".box-g-page span\" not found")

        movie.description = ''.join(map(lambda p_tag: p_tag.text, box_g_page.find_all('p'))).strip()
        if not movie.description:
            movie.description = ' '
            print_warning("Description not found")

        movie.production = self.find_between(details.text, 'Produkcja:', '\r\n\t').strip()
        if not movie.production:
            movie.production = ' '
            print_warning("Production not found")

        movie.genre = self.find_between(details.text, 'Gatunek:', ', Czas').strip()
        if not movie.genre:
            movie.genre = ' '
            print_warning("Genre not found")

        try:
            movie.duration = timedelta(minutes=float(self.find_between(details.text, 'Czas:', 'min').strip()))
        except ValueError:
            pass

        return movie

    @staticmethod
    def find_between(s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ''
