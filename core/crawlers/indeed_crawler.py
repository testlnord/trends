import io
import logging
import PIL
import datetime
from PIL import Image, ImageOps
import core.utils.internet.internet
from core.utils.ocr.mytess import MyTess


class IndeedCrawler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tesser = MyTess('pindeed')

        # CONSTANTS
        self.LEFT_BOTTOM_LINE_COLOR = (128, 128, 128)
        self.RIGHT_TOP_LINE_COLOR = (192, 192, 192)
        self.VALUES_COLOR = (255, 102, 0)

    def get_data(self, name) -> list:
        self.logger.info("Getting indeed plot: %s", name)
        image = self._get_image(name)
        result = self._parse_image(image)
        return result

    def _get_image(self, name):
        url = "http://www.indeed.com/trendgraph/jobgraph.png?q=%22{}%22".format(name.replace(' ', '+'))
        self.logger.debug("Getting image from url: %s", url)
        img_data = core.utils.internet.internet.get_from_url(url, binary=True)
        return Image.open(io.BytesIO(img_data), 'r')

    def _parse_image(self, image: Image) -> list:
        """
        Extracts values from Indeed trends plot image
        @type image: Image
        :param image: PIL image
        :return: list of (date, value) pairs
        """

        # looking for left and right borders of plot
        left_line_x, right_line_x = self._extract_vertical_lines(image)

        # looking for top and bottom borders of plot
        top_line_y, bottom_line_y = self._extract_horizontal_lines(image)

        # looking for ticks on vertical axis
        y_ticks = self._extract_ticks_on_vertical_axis(image, left_line_x)
        percents = self._extract_percents(image, y_ticks, left_line_x)

        # looking for ticks on horizontal axis
        x_ticks = self._extract_ticks_on_horizontal_axis(image, bottom_line_y)
        years = self._extract_years(image, x_ticks, bottom_line_y)

        return self._extract_values(image, percents, years)

    def _extract_vertical_lines(self, image: Image) -> tuple:
        left_x = right_x = 0
        best_left = best_right = 0

        for x in range(int(image.width / 2)):
            v_sum_left = 0
            for y in range(image.height):
                if image.getpixel((x, y)) == self.LEFT_BOTTOM_LINE_COLOR:
                    v_sum_left += 1
            if v_sum_left > best_left:
                best_left = v_sum_left
                left_x = x
            if best_left > image.height / 2:  # optimization
                break

        for x in range(image.width - 1, int(image.width / 2), -1):
            v_sum_right = 0
            for y in range(image.height):
                if image.getpixel((x, y)) == self.RIGHT_TOP_LINE_COLOR:
                    v_sum_right += 1
            if v_sum_right > best_right:
                best_right = v_sum_right
                right_x = x
            if best_right > image.height / 2:  # optimization
                break

        return left_x, right_x

    def _extract_horizontal_lines(self, image: Image) -> tuple:
        top_y = bottom_y = 0
        best_top = best_bottom = 0

        for y in range(int(image.height / 2)):
            h_sum_t = 0
            for x in range(image.width):
                if image.getpixel((x, y)) == self.RIGHT_TOP_LINE_COLOR:
                    h_sum_t += 1
            if h_sum_t > best_top:
                best_top = h_sum_t
                top_y = y
            if best_top > image.width / 2:  # optimization
                break

        for y in range(image.height - 1, int(image.height / 2), -1):
            h_sum_b = 0
            for x in range(image.width):
                if image.getpixel((x, y)) == self.LEFT_BOTTOM_LINE_COLOR:
                    h_sum_b += 1
            if h_sum_b > best_bottom:
                best_bottom = h_sum_b
                bottom_y = y
            if best_bottom > image.width / 2:  # optimization
                break

        return top_y, bottom_y

    def _extract_ticks_on_vertical_axis(self, image: Image, left_line_x: int) -> list:
        ticks = []
        for y in range(image.height):
            if image.getpixel((left_line_x - 1, y)) == image.getpixel((left_line_x - 2, y)) \
                    == self.LEFT_BOTTOM_LINE_COLOR:
                ticks.append(y)
        return ticks

    def _extract_ticks_on_horizontal_axis(self, image: Image, bottom_line_y: int) -> list:
        ticks = []
        for x in range(image.width):
            if image.getpixel((x, bottom_line_y + 1)) == image.getpixel((x, bottom_line_y + 2)) \
                    == self.LEFT_BOTTOM_LINE_COLOR:
                ticks.append(x)
        return ticks

    def _extract_percents(self, image, y_ticks, left_line_x) -> list:
        percents = []
        for tick in y_ticks:
            # todo 25 here is hardcoded and bug-prone estimation.
            # In fact we need to look for white strips from left to right.
            # First such stripe will be border of image and second border of percents. Its right-x coordinate is what we need here

            box = (25, tick - 5, left_line_x - 3, tick + 5)
            region = image.crop(box)

            text = region.crop(ImageOps.invert(region.convert('RGB')).getbbox())
            # debug
            # region.save(str(tick)+'.bmp')
            word = ''
            leftmost_unread_pixel = 0
            while leftmost_unread_pixel < text.width:
                x_left = leftmost_unread_pixel
                x_right = leftmost_unread_pixel + self.tesser.max_width
                if x_right > text.width:
                    x_right = text.width
                glyph = Image.new('RGBA', (x_right - x_left, 8), (255, 255, 255))
                glyph.paste(text.crop((x_left, 0, x_right, 8)))
                letter, width = self.tesser.tess(glyph)
                word += letter
                leftmost_unread_pixel += width
            percents.append((float(word), tick))

        return sorted(percents)

    def _extract_years(self, image: Image, x_ticks: list, bottom_line_y: int) -> list:
        years = []
        for tick in x_ticks:
            # this 15s is bugprone estimations
            # todo  fairly find gaps bw words

            box = (tick - 15, bottom_line_y + 3, tick + 20, image.height)
            region = image.crop(box)

            text = region.crop(ImageOps.invert(region.convert('RGB')).getbbox())
            # debug
            # region.save(str(tick)+'.bmp')
            word = ''
            rightmost_unread_pixel = text.width
            while rightmost_unread_pixel > 0:
                x_left = rightmost_unread_pixel - self.tesser.max_width
                if x_left < 0:
                    x_left = 0
                x_right = rightmost_unread_pixel
                glyph = Image.new('RGBA', (x_right - x_left, 8), (255, 255, 255))
                glyph.paste(text.crop((x_left, 0, x_right, 8)))
                letter, width = self.tesser.tess(glyph, left=False)
                word = letter + word
                rightmost_unread_pixel -= width
            years.append((self._word_to_year(word), tick))

        years = sorted(years)
        # add first and last years
        min_year_0 = years[0]
        min_year_1 = years[1]
        first_year = (min_year_0[0] - 1, min_year_0[1] - (min_year_1[1] - min_year_0[1]))

        max_year_n1 = years[-2]
        max_year_n = years[-1]
        last_year = (max_year_n[0] + 1, max_year_n[1] + (max_year_n[1] - max_year_n1[1]))

        return [first_year] + years + [last_year]

    def _word_to_year(self, word: str) -> int:
        if not word.startswith('an'):
            self.logger.warning('Strange year: %s', word)
        year = 2000 + int(word[2:].strip())
        return year

    def _extract_values(self, image, percents, years):
        prev_year, prev_tick = years[0]
        values = []
        for year, tick in years[1:]:
            month_step = (tick-prev_tick)/12
            for month in range(1,13):
                mx = int(prev_tick + month_step*(month-1))
                value_ys = []
                for y in range(image.height):
                    if image.getpixel((mx, y)) == self.VALUES_COLOR:
                        value_ys.append(y)

                if value_ys:
                    avg_y = sum(value_ys)/len(value_ys)
                    value = self._coord_to_value(avg_y, percents)
                    date = datetime.date(year, month, 1)
                    values.append((date, value))
            prev_tick, prev_year = tick, year
        return values


    def _coord_to_value(self, y, percents):
        prev_perc, prev_tick = percents[0]
        if y > prev_tick:
            perc, tick = percents[1]
            return prev_perc + ((prev_tick-y)/(tick-prev_tick))*(prev_perc - perc)

        for perc, tick in percents[1:]:
            if prev_tick <= y < tick:
                return prev_perc + ((prev_tick - y)/(prev_tick - tick))*(perc - prev_perc)
            prev_perc, prev_tick = perc, tick

        # if we haven't terminated than y >= max(tick) and prev_tick = max(tick)
        perc_n1, tick_n1 = percents[-2]
        return prev_perc + ((prev_tick - y)/(tick_n1 - prev_tick))*(prev_perc - perc_n1)



