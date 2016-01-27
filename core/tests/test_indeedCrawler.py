""" """
from unittest import TestCase
import datetime

from core.crawlers.indeed_crawler import IndeedCrawler
from PIL import Image
import os


class TestIndeedCrawler(TestCase):
    def setUp(self):
        self.dir = os.path.dirname(__file__)
        self.crawler = IndeedCrawler()
        self.test_image1 = Image.open(os.path.join(self.dir, "ind_testimg1.png"))
        self.test_image2 = Image.open(os.path.join(self.dir, "ind_testimg2.png"))

    def test__get_vertical_line(self):
        left_line, right_line = self.crawler._extract_vertical_lines(self.test_image1)
        self.assertEqual(left_line, 50)
        self.assertEqual(right_line, 532)
        left_line, right_line = self.crawler._extract_vertical_lines(self.test_image2)
        self.assertEqual(left_line, 56)
        self.assertEqual(right_line, 532)

    def test__get_horizontal_line(self):
        top_line, bottom_line = self.crawler._extract_horizontal_lines(self.test_image1)
        self.assertEqual(top_line, 43)
        self.assertEqual(bottom_line, 280)
        top_line, bottom_line = self.crawler._extract_horizontal_lines(self.test_image2)
        self.assertEqual(top_line, 43)
        self.assertEqual(bottom_line, 280)

    def test__get_ticks_vertical(self):
        ticks = self.crawler._extract_ticks_on_vertical_axis(self.test_image1, 50)
        self.assertEqual(len(ticks), 5)
        ticks = self.crawler._extract_ticks_on_vertical_axis(self.test_image2, 56)
        self.assertEqual(len(ticks), 3)

    def test__get_ticks_horizontal(self):
        ticks = self.crawler._extract_ticks_on_horizontal_axis(self.test_image1, 280)
        self.assertEqual(len(ticks), 10)
        ticks = self.crawler._extract_ticks_on_horizontal_axis(self.test_image2, 280)
        self.assertEqual(len(ticks), 10)

    def test__extract_percents(self):
        y_line = 50
        ticks = self.crawler._extract_ticks_on_vertical_axis(self.test_image1, y_line)
        percents = self.crawler._extract_percents(self.test_image1, ticks, y_line)
        self.assertEqual(sorted(percents), [(0, 280), (0.1, 222), (0.2, 164), (0.3, 107), (0.4, 49)])
        y_line = 56
        ticks = self.crawler._extract_ticks_on_vertical_axis(self.test_image2, y_line)
        percents = self.crawler._extract_percents(self.test_image2, ticks, y_line)
        self.assertEqual(sorted(percents), [(0, 280), (0.02, 197), (0.04, 115)])

    def test__extract_years(self):
        x_line = 280
        ticks = self.crawler._extract_ticks_on_horizontal_axis(self.test_image1, x_line)
        years = self.crawler._extract_years(self.test_image1, ticks, x_line)
        self.assertEqual(sorted(x[0] for x in years),
                         [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016])
        x_line = 280
        ticks = self.crawler._extract_ticks_on_horizontal_axis(self.test_image2, x_line)
        years = self.crawler._extract_years(self.test_image2, ticks, x_line)
        self.assertEqual(sorted(x[0] for x in years),
                         [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016])

    def test__coord_to_value(self):
        percents = [(1, 20), (2, 10)]
        y = [5, 10, 15, 20, 25]
        expected_v = [2.5, 2, 1.5, 1, 0.5]
        for i, y in enumerate(y):
            v = self.crawler._coord_to_value(y, percents)
            self.assertAlmostEqual(v, expected_v[i])
