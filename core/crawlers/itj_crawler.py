"""crawler for ITjobs """

import logging
from PIL import ImageOps
from PIL import Image
import datetime
import io
import numpy
from ..utils.internet import internet
from ..utils.ocr.mytess import tess_digit, tess_percents, eqdist


class ItjCrawler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_data(self, name) -> list:
        self.logger.info("Getting itjobs plot: %s", name)
        image = self._get_image(name)
        result = self._parse_image(image)
        return result

    @staticmethod
    def _get_image(name):
        query = '+'.join(name.split(' '))
        url = "http://www.itjobswatch.co.uk/charts/permanent-demand-trend.aspx?s=" + query + "&l=uk"
        data = internet.get_from_url(url, binary=True)
        return Image.open(io.BytesIO(data), 'r')

    def years_from_image(self, image):
        # getting years
        years = []
        for x1, x2, y in self.get_year_coord(image):
            box = (x1 + 1, y - 7, x2, y + 7)
            region = image.crop(box)
            x = 0
            while region.getpixel((x, 7)) == (0, 0, 0, 255):
                region.putpixel((x, 7), (255, 255, 255, 255))
                x += 1
            x = region.size[0] - 1
            while region.getpixel((x, 7)) == (0, 0, 0, 255):
                region.putpixel((x, 7), (255, 255, 255, 255))
                x -= 1

            text = region.crop(ImageOps.invert(region.convert('RGB')).getbbox())
            word = ''
            for x in range(0, text.size[0], 6):
                glyph = Image.new('RGBA', (6, 8), (255, 255, 255, 255))
                glyph.paste(text.crop((x, 0, x + 6, 8)))
                # have some issues with last ones, they crops and
                # starts to have (0,0,0,0)-colored stripe
                #   little hack to eliminate it
                data = numpy.array(glyph)  # "data" is a height x width x 4 numpy array
                red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability
                # Replace zeros with white...
                zero_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 0)
                data[...][zero_areas.T] = (255, 255, 255, 255)
                glyph = Image.fromarray(data)

                word += tess_digit(glyph).splitlines()[0]

            years.append((x1, x2, int(word)))
        if not years:
            self.logger.warning("No years on image")
            raise ValueError("bad image")
        # add first year:
        l, r, year = years[0]
        years = [(l - (r - l), l, year - 1)] + years
        # add current year
        l, r, year = years[-1]
        years.append((r, r + (r - l), year + 1))
        self.logger.debug("Years on image %s", str(years))
        return years

    def _parse_image(self, image):
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

    def get_year_coord(self, image):
        # get line coord
        line_y = None

        # looking for horizontal line
        max_black_pixels = 0
        for y in range(310, 290, -1):
            black_pixels = 0
            for x in range(0, image.size[0]):
                if image.getpixel((x, y)) == (0, 0, 0, 255):
                    black_pixels += 1
            if black_pixels > max_black_pixels or line_y is None:
                max_black_pixels = black_pixels
                line_y = y

        if max_black_pixels < 100:
            self.logger.info("Nonstandart image. Can't find horizontal line in the bottom. Will try middles approach.")
            # raise ValueError("Bad image. Can't find horizontal line in the bottom.")
            yield from self.get_year_borders(image, 285, 12, middles=True)
        self.logger.debug("Founded horizontal line %s with %s black pixels", line_y, max_black_pixels)

        yield from self.get_year_borders(image, line_y, 7)

    def get_year_borders(self, image, line_y, ticks_shift, middles=False):
        # get year borders
        prev_x = None
        for x in range(20, 615):
            if image.getpixel((x, line_y - ticks_shift)) == (0, 0, 0, 255):
                if prev_x is not None:
                    if middles:
                        yield (int(x-(x-prev_x)/2), int(x+(x-prev_x)/2), line_y)
                    else:
                        yield (prev_x, x, line_y)
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
                    for y in range(image.size[1]):
                        if eqdist(image.getpixel((x, y)), (250, 150, 5, 255)) < 20:  # MAGIC THRESHOLD orange color
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
