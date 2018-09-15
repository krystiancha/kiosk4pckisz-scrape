import unittest

from kiosk4pckisz_scrape.scrapers import MovieShowScraper


class MyTestCase(unittest.TestCase):
    def test_something(self):
        titles = [
            ('MOJA ŻYRAFA - Poranek, Małe kino', 'MOJA ŻYRAFA', 1),
            ('UPROWADZONA KSIĘŻNICZKA - Małe kino', 'UPROWADZONA KSIĘŻNICZKA', 1),
            ('BIAŁY KIEŁ', 'BIAŁY KIEŁ', 0),
            ('JULIUSZ - Małe kino', 'JULIUSZ', 1),
            ('JULIUSZ', 'JULIUSZ', 0),
            ('DYWIZJON 303. HISTORIA PRAWDZIWA', 'DYWIZJON 303. HISTORIA PRAWDZIWA', 0),
            ('ZAKONNICA - Małe kino', 'ZAKONNICA', 1),
            ('MISSION: IMPOSSIBLE - FALLOUT', 'MISSION: IMPOSSIBLE - FALLOUT', 0),
            ('SOLDAU. MIASTO NA POGRANICZU ŚMIERCI - Małe kino', 'SOLDAU. MIASTO NA POGRANICZU ŚMIERCI', 1),
            ('WYSZCZEKANI - Małe kino', 'WYSZCZEKANI', 1),
        ]
        for title in titles:
            self.assertEqual(MovieShowScraper.parse_title(title[0]), title[1:])


if __name__ == '__main__':
    unittest.main()
