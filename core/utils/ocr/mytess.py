""" My Tesseract.

Couple of functions to parse image fragments to text
"""

import os

__author__ = 'user'

from PIL import Image, ImageOps
import numpy


def eqdist(vec1, vec2):
    return numpy.linalg.norm(numpy.array(vec1) - numpy.array(vec2))


def tess_number(bbox, image):
    region = image.crop(bbox)
    x = 0
    while region.getpixel((x, 7)) == (0, 0, 0, 255):
        region.putpixel((x, 7), (255, 255, 255, 255))
        x += 1
    x = region.size[0] - 1
    while region.getpixel((x, 7)) == (0, 0, 0, 255):
        region.putpixel((x, 7), (255, 255, 255, 255))
        x -= 1

    text = region.crop(ImageOps.invert(region.convert('RGB')).getbbox())
    # debug image output
    # text.save(image.filename + str(bbox) + '.png')
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
    return int(word)


def tess_percents(image):
    """image -- PIL or Pillow image
    """
    text = image.crop(ImageOps.invert(image.convert('RGB')).getbbox())
    left_unrecognized_border = 0
    glyph_path = os.path.join(os.path.dirname(__file__), 'digit_glyphs', 'p10')
    line = ""
    while left_unrecognized_border < text.size[0]:
        # recognize one symbol
        similarity = []
        for glyph_file in (file_name for file_name in os.listdir(glyph_path) if file_name.endswith('.png')):
            glyph = Image.open(os.path.join(glyph_path, glyph_file))
            if glyph.size[0] > text.size[0] - left_unrecognized_border:
                continue
            h1 = text.crop(
                (left_unrecognized_border, 0, left_unrecognized_border + glyph.size[0], text.size[1])).histogram()
            h2 = glyph.histogram()
            similarity.append((glyph_file[0], eqdist(h1, h2), glyph.size[0]))
        if not similarity:
            break
        symbol = min(similarity, key=lambda x: x[1])
        line += symbol[0]
        left_unrecognized_border += symbol[2]
    return line


def tess_digit(image):
    """image -- PIL or Pillow image"""
    glyph_path = os.path.join(os.path.dirname(__file__), 'digit_glyphs', 'p8')
    values = []

    h1 = image.histogram()
    for file in os.listdir(glyph_path):
        h2 = Image.open(os.path.join(glyph_path, file)).histogram()
        rms = eqdist(h1, h2)
        values.append((file[0], rms))
    val = min(values, key=lambda x: x[1])
    return val[0]


class MyTess:
    def __init__(self, path_to_glyphs):
        self.glyph_path = os.path.join(os.path.dirname(__file__), 'digit_glyphs', path_to_glyphs)
        self.glyphs = []
        self.max_width = 0
        for glyph_name in os.listdir(self.glyph_path):
            if glyph_name.endswith('.png'):
                glyph_image = Image.open(os.path.join(self.glyph_path, glyph_name))
                if self.max_width < glyph_image.size[0]:
                    self.max_width = glyph_image.size[0]
                self.glyphs.append((glyph_name[:-4], glyph_image.size[0], glyph_image.histogram()))
                glyph_image.close()
                # todo nice to have check that all glyphs has different histograms

    def tess(self, image, left=True):
        text_hists = {}
        values = []
        for name, w, hist in self.glyphs:
            try:
                text_hist = text_hists[w]
            except KeyError:
                if left:
                    box = (0, 0, w, image.size[1])
                else:
                    box = (image.size[0] - w, 0, image.size[0], image.size[1])
                region = image.crop(box)
                text_hist = region.histogram()
                text_hists[w] = text_hist
            rms = eqdist(hist, text_hist)
            values.append((rms, name, w))
        best_match = min(values, key=lambda x: (round(x[0], 5), -x[2]))
        if best_match[0] > 1:
            return '', 1
        return best_match[1], best_match[2]
