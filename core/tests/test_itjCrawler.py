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
        self.test_image1 = Image.open(os.path.join(self.dir, "itj_testimg_new1.png"))
        self.test_image2 = Image.open(os.path.join(self.dir, "itj_testimg_new2.png"))
        self.test_image3 = Image.open(os.path.join(self.dir, "itj_testimg_new3.png"))


    def test__parse_image(self):
        self.assertEqual(len(self.crawler._parse_image(self.test_image1)), 127)
        self.assertEqual(len(self.crawler._parse_image(self.test_image2)), 122)

    def test_get_percent_coord(self):
        self.assertListEqual(list(self.crawler.get_percent_coord(self.test_image1)),
                             [10, 76, 141, 206, 272])
        self.assertListEqual(list(self.crawler.get_percent_coord(self.test_image2)),
                             [10, 43, 76, 108, 141, 174, 206, 239, 272])

    def test_get_year_coord(self):
        self.assertListEqual(list(self.crawler.get_year_coord(self.test_image1)),
                             [(72, 172, 304),  (172, 273, 304),  (273, 373, 304),  (373, 474, 304),  (474, 575, 304)])
        self.assertListEqual(list(self.crawler.get_year_coord(self.test_image2)),
                             [(45, 93, 285), (93, 141, 285), (140, 187, 285), (188, 236, 285), (236, 284, 285),
                              (284, 332, 285), (331, 378, 285), (379, 427, 285), (427, 475, 285),
                              (475, 523, 285), (523, 571, 285), (570, 617, 285)])

    def test_years_from_image(self):
        self.assertListEqual(self.crawler.years_from_image(self.test_image1),
                             [(-28, 72, 2010),  (72, 172, 2011),  (172, 273, 2012),  (273, 373, 2013),  (373, 474, 2014),  (474, 575, 2015) , (575, 676, 2016)])
        self.assertListEqual(self.crawler.years_from_image(self.test_image2),
                             [(-3, 45, 2004), (45, 93, 2005), (93, 141, 2006), (140, 187, 2007), (188, 236, 2008),
                              (236, 284, 2009), (284, 332, 2010), (331, 378, 2011), (379, 427, 2012),
                              (427, 475, 2013), (475, 523, 2014), (523, 571, 2015), (570, 617, 2016), (617, 664, 2017)])
        self.assertListEqual(self.crawler.years_from_image(self.test_image3),
                             [(-54, 98, 2012), (98, 250, 2013), (250, 403, 2014), (403, 555, 2015), (555, 707, 2016)])

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
        data = self.crawler._parse_image(self.test_image3)
        self.assertEqual(max(data, key=lambda x:x[0])[0].year, 2016)