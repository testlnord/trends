""" My Tesseract.

Couple of functions to parse image fragments to text
"""

import os

__author__ = 'user'

from PIL import Image, ImageOps
import numpy


def eqdist(vec1, vec2):
    return numpy.linalg.norm(numpy.array(vec1) - numpy.array(vec2))


def tess_percents(image):
    """image -- PIL or Pillow image
    """
    text = image.crop(ImageOps.invert(image.convert('RGB')).getbbox())
    left_unrecognized_border = 0
    glyph_path = os.path.join(os.path.dirname(__file__), 'digit_glyphs', 'p9')
    line = ""
    while left_unrecognized_border < text.size[0]:
        # recognize one symbol
        similarity = []
        for glyph_file in os.listdir(glyph_path):
            glyph = Image.open(os.path.join(glyph_path, glyph_file))
            if glyph.size[0] > text.size[0] - left_unrecognized_border:
                continue
            h1 = text.crop(
                (left_unrecognized_border, 0, left_unrecognized_border + glyph.size[0], text.size[1])).histogram()
            h2 = glyph.histogram()
            similarity.append((glyph_file[0], eqdist(h1, h2), glyph.size[0]))
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