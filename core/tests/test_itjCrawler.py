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

    def test__parse_image(self):
        self.assertEqual(len(self.crawler._parse_image(self.test_image1)), 127)
        self.assertEqual(len(self.crawler._parse_image(self.test_image2)), 122)

    def test_get_percent_coord(self):
        self.assertListEqual(list(self.crawler.get_percent_coord(self.test_image1)),
                             [9, 38, 67, 95, 124, 153, 182, 211, 239])
        self.assertListEqual(list(self.crawler.get_percent_coord(self.test_image2)),
                             [9, 47, 86, 124, 163, 201, 239])

    def test_get_year_coord(self):
        self.assertListEqual(list(self.crawler.get_year_coord(self.test_image1)),
                             [(76, 132, 271), (132, 187, 271), (187, 243, 271), (243, 299, 271), (299, 354, 271),
                              (354, 410, 271), (410, 466, 271), (466, 521, 271), (521, 577, 271)])
        self.assertListEqual(list(self.crawler.get_year_coord(self.test_image2)),
                             [(55, 112, 271), (112, 170, 271), (170, 228, 271), (228, 286, 271), (286, 344, 271),
                              (344, 402, 271), (402, 460, 271), (460, 518, 271), (518, 576, 271)])

    def test_years_from_image(self):
        self.assertListEqual(self.crawler.years_from_image(self.test_image1),
                             [(20, 76, 2004), (76, 132, 2005), (132, 187, 2006), (187, 243, 2007), (243, 299, 2008), (299, 354, 2009),
                              (354, 410, 2010), (410, 466, 2011), (466, 521, 2012), (521, 577, 2013), (577, 633, 2014)])
        self.assertListEqual(self.crawler.years_from_image(self.test_image2),
                             [(-2, 55, 2004), (55, 112, 2005), (112, 170, 2006), (170, 228, 2007), (228, 286, 2008), (286, 344, 2009),
                              (344, 402, 2010), (402, 460, 2011), (460, 518, 2012), (518, 576, 2013), (576, 634, 2014)])
        self.assertListEqual(self.crawler.years_from_image(self.test_image3),
                             [(-21, 42, 2006), (42, 105, 2007), (105, 168, 2008), (168, 231, 2009), (231, 294, 2010), (294, 358, 2011),
                              (358, 421, 2012), (421, 484, 2013), (484, 547, 2014), (547, 610, 2015), (610, 673, 2016)])

    def test_y2value(self):
        self.assertEqual(self.crawler.y2value(10, [(0, 0), (20, 100.0)]), 50)

    def test_x2date(self):
        self.assertLess(self.crawler.x2date(10, [(0, 20, 2000)]) - datetime.date(2000, 7, 1),
                        datetime.timedelta(days=2))
        self.assertLess(self.crawler.x2date(10, [(10, 20, 2000)]) - datetime.date(2000, 1, 1),
                        datetime.timedelta(days=2))
        self.assertLess(self.crawler.x2date(0, [(10, 20, 2000)]) - datetime.date(1999, 1, 1),
                        datetime.timedelta(days=2))