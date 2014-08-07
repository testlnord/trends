import datetime

__author__ = 'user'


from core.parsers.parser import Parser
import urllib.request as ur
from PIL import ImageOps
import tesserwrap
from core.parsers.mytess import *
import numpy




class ItjobsParser(Parser):
    init_dir = "data/itjobs"

    def get_response(self, query):
        query = '+'.join(query.split(' '))
        url = "http://www.itjobswatch.co.uk/charts/permanent-demand-trend.aspx?s="+query+"&l=uk"
        user_agent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
        headers = {'User-Agent': user_agent}
        req = ur.Request(url, headers=headers)
        response = ur.urlopen(req)
        data = response.read()
        return data

    @staticmethod
    def get_percent_coord(image):
        for y in range(image.size[1]):
            if image.getpixel((615, y)) == (0, 0, 0, 255):
                yield y
        raise StopIteration()

    @staticmethod
    def get_year_coord(image):
        #get line coord
        line_y = 0
        for y in range(image.size[1] - 1, 0, -1):
            if image.getpixel((25, y)) == (0, 0, 0, 255):
                line_y = y
                break

        #get year borders
        prev_x = None
        for x in range(20, 615):
            if image.getpixel((x, line_y - 2)) == (0, 0, 0, 255):
                if prev_x is not None:
                    yield (prev_x, x, y)
                prev_x = x
        raise StopIteration()

    @staticmethod
    def get_data_point(image, years):
        # pre tail
        l, r, year = years[0]
        for x in range(12):
            date = datetime.date(year - 1, 12 - x, 1)
            c_year = datetime.date(year, 1, 1)
            x = l + int((date - c_year).total_seconds()
                        / (datetime.date(year + 1, 1, 1) - c_year).total_seconds()*(r-l))
            pts = []
            for y in range(image.size[1]):
                if eqdist(image.getpixel((x, y)), (250, 150, 5, 255)) < 10:  # MAGIC THRESHOLD orange color
                    pts.append(y)

            if pts:
                y = sum(pts)/len(pts)
                yield (x, y, date)
        # data bw years
        for l, r, year in years:
            for x in range(12):
                date = datetime.date(year, x + 1, 1)
                c_year = datetime.date(year, 1, 1)
                x = l + int((date - c_year).total_seconds()
                            / (datetime.date(year + 1, 1, 1) - c_year).total_seconds()*(r-l))
                pts = []
                for y in range(image.size[1]):
                    if eqdist(image.getpixel((x, y)), (250, 150, 5, 255)) < 10:  # MAGIC THRESHOLD orange color
                        pts.append(y)

                if pts:
                    y = sum(pts)/len(pts)
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
            d = d1 + (d2-d1)*(x - x1)/(x2 - x1)
            if d > datetime.datetime.now().date():
                raise RuntimeError((x, d, years))
            return d

        for x1, x2, year in years:
            if x1 <= x < x2:
                d1 = datetime.date(year, 1, 1)
                d2 = datetime.date(year + 1, 1, 1)
                d = d1 + (d2-d1)*(x - x1)/(x2 - x1)
                if d > datetime.datetime.now().date():
                    raise RuntimeError((x, d, years))
                return d

    def get_raw_data(self, response):
        im = Image.open(io.BytesIO(response), 'r')
        tr = tesserwrap.Tesseract(datadir="/usr/share/tesseract-ocr")
        tr.set_page_seg_mode(mode=tesserwrap.PageSegMode().PSM_SINGLE_WORD)

        tr.set_variable('tessedit_char_whitelist', '0123456789.%')

        #getting percents
        percents = []
        for y in self.get_percent_coord(im):
            box = (620, y - 7, 670, y + 7)
            region = im.crop(box)
            val = tess_percents(region)[:-1]
            percents.append((y, float(val)))

        #getting years
        years = []
        for x1, x2, y in self.get_year_coord(im):
            box = (x1+1, y - 7, x2, y + 7)
            region = im.crop(box)
            x = 0
            while region.getpixel((x, 7)) == (0, 0, 0, 255):
                region.putpixel((x, 7), (255, 255, 255, 255))
                x += 1
            x = region.size[0]-1
            while region.getpixel((x, 7)) == (0, 0, 0, 255):
                region.putpixel((x, 7), (255, 255, 255, 255))
                x -= 1

            text = region.crop(ImageOps.invert(region.convert('RGB')).getbbox())
            word = ''
            for x in range(0, text.size[0], 6):
                glyph = Image.new('RGBA', (6, 8), (255, 255, 255, 255))
                glyph.paste(text.crop((x, 0, x + 6, 8)))
                #have some issues with last ones, they crops and
                #starts to have (0,0,0,0)-colored stripe
                #little hack to eliminate it
                data = numpy.array(glyph)   # "data" is a height x width x 4 numpy array
                red, green, blue, alpha = data.T  # Temporarily unpack the bands for readability
                # Replace zeros with white...
                zero_areas = (red == 0) & (blue == 0) & (green == 0) & (alpha == 0)
                data[...][zero_areas.T] = (255, 255, 255, 255)
                glyph = Image.fromarray(data)

                if x1 == 414:
                    glyph.save(str(x)+'_' + str(x1)+'.png', 'PNG')

                word += tess_digit(glyph).splitlines()[0]

            years.append((x1, x2, int(word)))

        #getting data points
        result = []
        for x, y, d in self.get_data_point(im, years):
            v = self.y2value(y, percents)
            #d = self.x2date(x, years)

            result.append((d, v))
        print(result)
        return result




