"""crawler for ITjobs """

import logging
from PIL import ImageOps
from PIL import Image
import datetime
import io
import numpy
from ..utils.internet import internet
from ..utils.ocr.mytess import tess_number, tess_percents, eqdist


class ItjCrawler:
    YEARS_ONLY_PLOT = 1
    YEARS_AND_MONTHS_PLOT = 2

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_data(self, name) -> list:
        self.logger.info("Getting itjobs plot: %s", name)
        image = self._get_image(name)
        result = self.parse_image(image)
        return result

    @staticmethod
    def _get_image(name):
        query = '+'.join(name.split(' '))
        url = "http://www.itjobswatch.co.uk/charts/permanent-demand-trend.aspx?s=" + query + "&l=uk"
        data = internet.get_from_url(url, binary=True)
        return Image.open(io.BytesIO(data), 'r')

    def get_years_bboxes(self, year_ticks, years_axis, plot_type):
        if plot_type == self.YEARS_ONLY_PLOT:
            return ((x1 - 18, years_axis + 5, x1 + 18, years_axis + 19) for x1, _ in year_ticks)
        else:
            return ((x1+1, years_axis - 7, x2, years_axis + 7) for x1, x2 in year_ticks)


    def years_from_image(self, image):
        # getting years
        years_axis, plot_type = self.get_years_axis(image)
        # depending on plot type ticks may be bellow or above years axis
        ticks_shift = -1 if plot_type == self.YEARS_ONLY_PLOT else 3
        years_ticks = list(self.get_year_ticks(years_axis, ticks_shift, image))

        years_label_bboxes = self.get_years_bboxes(years_ticks, years_axis, plot_type)
        years = [ tess_number(bbox, image) for bbox in years_label_bboxes ]
        if not years:
            self.logger.warning("No years on image")
            raise ValueError("bad image")

        years_with_intervals = [(x1, x2, year) for (x1, x2), year in zip(years_ticks, years)]

        # add first year:
        l, r, year = years_with_intervals[0]
        years_with_intervals = [(l - (r - l), l, year - 1)] + years_with_intervals
        # add current year
        l, r, year = years_with_intervals[-1]
        years_with_intervals.append((r, r + (r - l), year + 1))
        self.logger.debug("Years on image %s", str(years_with_intervals))
        return years_with_intervals

    def parse_image(self, image):
        # getting percents
        percents = []
        for y in self.get_percent_coord(image):
            box = (620, y - 7, 670, y + 7)
            region = image.crop(box)
            val = tess_percents(region)[:-1]
            percents.append((y, float(val)))

        years = self.years_from_image(image)
        # getting data points
        result = []
        for x, y, d in self.get_data_point(image, years):
            v = self.y2value(y, percents)
            # d = self.x2date(x, years)

            result.append((d, v))

        self.logger.debug(result)
        return result

    @staticmethod
    def get_percent_coord(image):
        for y in range(image.size[1]):
            if image.getpixel((615, y)) == image.getpixel((614, y)) == image.getpixel((616, y)) == (0, 0, 0, 255):
                yield y
        raise StopIteration()

    def get_years_axis(self, image):
        # get line coord
        line_y = None
        # looking for horizontal line
        max_black_pixels = 0
        ENOUGH_NUMBER_OF_BLACK_PIXELS = 200
        for y in range(320, 260, -1):
            black_pixels = 0
            for x in range(0, image.size[0]):
                if image.getpixel((x, y)) == (0, 0, 0, 255):
                    black_pixels += 1
            if black_pixels >= ENOUGH_NUMBER_OF_BLACK_PIXELS:
                max_black_pixels = black_pixels
                line_y = y
                break
        if max_black_pixels < 100:
            self.logger.info("Nonstandart image. Can't find horizontal line in the bottom. Will try middles approach.")
            raise ValueError("Bad image. Can't find horizontal line in the bottom.")
        self.logger.debug("Founded horizontal line %s with %s black pixels", line_y, max_black_pixels)
        return line_y, self.YEARS_ONLY_PLOT if max_black_pixels > 550 else self.YEARS_AND_MONTHS_PLOT

    def get_year_ticks(self, line_y, ticks_shift, image):
        # get year borders
        prev_x = None
        for x in range(20, 615):
            y = line_y - ticks_shift
            color = image.getpixel((x, y))
            if color == (0, 0, 0, 255):
                if prev_x is not None:
                    yield (prev_x, x)
                prev_x = x
        raise StopIteration()

    @staticmethod
    def get_data_point(image, years):
        # data bw years
        for l, r, year in years:
            month_width = (r - l) / 12
            for m in range(12):
                date = datetime.date(year, m + 1, 1)
                c_year = datetime.date(year, 1, 1)
                x = l + int(round(month_width * m))
                pts = []
                try:
                    for y in range(272): # magic constant: lower bound of plots
                        if eqdist(image.getpixel((x, y)), (254, 152, 1, 255)) < 20:  # MAGIC THRESHOLD orange color
                            pts.append(y)
                except IndexError:
                    pts = []
                    pass  # if coord is out of image then just live pts array empty
                if pts:
                    y = sum(pts) / len(pts)
                    yield (x, y, date)
        raise StopIteration()

    @staticmethod
    def y2value(y, percents):
        if y >= percents[-1][0]:
            y_n, p_n = percents[-1]
            y_o, p_o = percents[-2]
            return p_o - (p_o - p_n) * (y - y_o) / (y_n - y_o)

        if y < percents[0][0]:
            y_n, p_n = percents[1]
            y_o, p_o = percents[0]
            return p_o - (p_o - p_n) * (y - y_o) / (y_n - y_o)

        for idx, (y_n, p_n) in enumerate(percents):
            if y_n > y:
                y_o, p_o = percents[idx - 1]
                return p_o - (p_o - p_n) * (y - y_o) / (y_n - y_o)

    @staticmethod
    def x2date(x, years):
        if x < years[0][0] or x >= years[-1][1]:
            x1, x2, year = years[0]
            d1 = datetime.date(year, 1, 1)
            d2 = datetime.date(year + 1, 1, 1)
            d = d1 + (d2 - d1) * (x - x1) / (x2 - x1)
            if d > datetime.datetime.now().date():
                raise RuntimeError((x, d, years))
            return d

        for x1, x2, year in years:
            if x1 <= x < x2:
                d1 = datetime.date(year, 1, 1)
                d2 = datetime.date(year + 1, 1, 1)
                d = d1 + (d2 - d1) * (x - x1) / (x2 - x1)
                if d > datetime.datetime.now().date():
                    raise RuntimeError((x, d, years))
                return d
