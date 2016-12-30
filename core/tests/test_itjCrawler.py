""" """
from unittest import TestCase
import datetime
from core.crawlers.itj_crawler import ItjCrawler
from PIL import Image
import os


class TestItjCrawler(TestCase):
    def setUp(self):
        self.dir = os.path.dirname(__file__)
        self.crawler = ItjCrawler()
        self.test_image1 = Image.open(os.path.join(self.dir, "testimg1.png"))
        self.test_image2 = Image.open(os.path.join(self.dir, "testimg2.png"))
        self.test_image3 = Image.open(os.path.join(self.dir, "testimg3.png"))
        self.test_image4 = Image.open(os.path.join(self.dir, "testimg4.png"))

    def test__parse_image(self):
        self.assertEqual(len(self.crawler.parse_image(self.test_image1)), 155)
        self.assertEqual(len(self.crawler.parse_image(self.test_image2)), 122)
        self.assertEqual(len(self.crawler.parse_image(self.test_image3)), 122)
        pass

    def test_get_percent_coord(self):
        self.assertListEqual(list(self.crawler.get_percent_coord(self.test_image1)),
                             [10, 48, 85, 122, 160, 197, 234, 272])
        self.assertListEqual(list(self.crawler.get_percent_coord(self.test_image4)),
                             [10, 76, 141, 206, 272])

    def test_check_plot_type(self):
        self.assertEqual(self.crawler.get_years_axis(self.test_image1), (272, ItjCrawler.YEARS_ONLY_PLOT))
        self.assertEqual(self.crawler.get_years_axis(self.test_image2), (301, ItjCrawler.YEARS_AND_MONTHS_PLOT))

    def test_get_year_coord(self):
        self.assertListEqual(list(self.crawler.get_year_ticks(272, -1, self.test_image1)),
                             [(63,109),(109,155),(155,200),(200,246),
                              (246,292),(292,338),(338,384),(384,429),(429,475),(475,521),(521,567)])
        self.assertListEqual(list(self.crawler.get_year_ticks(301, 3, self.test_image2)),
                             [(159,311), (311, 462)])


    def test_years_from_image(self):
        self.assertListEqual(self.crawler.years_from_image(self.test_image1),
                             [(17, 63, 2004), (63,109, 2005),(109,155, 2006),(155,200, 2007),(200,246, 2008),
                              (246,292, 2009),(292,338, 2010),(338,384, 2011),(384,429, 2012),
                              (429,475, 2013),(475,521, 2014),(521,567, 2015),(567, 613, 2016)])

        self.assertListEqual(self.crawler.years_from_image(self.test_image2),
                             [(7,159,2013), (159, 311, 2014), (311, 462, 2015), (462, 613, 2016)])

    def test_y2value(self):
        self.assertEqual(self.crawler.y2value(10, [(0, 0), (20, 100.0)]), 50)

    def test_x2date(self):
        self.assertLess(self.crawler.x2date(10, [(0, 20, 2000)]) - datetime.date(2000, 7, 1),
                        datetime.timedelta(days=2))
        self.assertLess(self.crawler.x2date(10, [(10, 20, 2000)]) - datetime.date(2000, 1, 1),
                        datetime.timedelta(days=2))
        self.assertLess(self.crawler.x2date(0, [(10, 20, 2000)]) - datetime.date(1999, 1, 1),
                        datetime.timedelta(days=2))

    def test_getData(self):
        data = self.crawler.parse_image(self.test_image3)
        self.assertEqual(max(data, key=lambda x: x[0])[0].year, 2016)
        pass
