from functools import reduce
import operator
import os
import math

__author__ = 'user'

import subprocess
import io
from PIL import Image
import numpy


def eqdist(vec1, vec2):
    return numpy.linalg.norm(numpy.array(vec1) - numpy.array(vec2))



def tess_percents(image):
    """image -- PIL or Pillow image"""
    image = image.resize(tuple(x*2 for x in image.size), Image.BICUBIC)
    file = io.BytesIO()
    image.save(file, 'PNG')
    subp = subprocess.Popen(['tesseract', 'stdin', 'stdout', '-psm=8', 'bazaar'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    res = subp.communicate(input=file.getvalue())
    res = res[0].decode()
    res = res.splitlines()[0]
    res = res.replace(' ', '')
    if res[-1] != '%' and res.endswith('96'):
        res = res[:-2] + '%'
    return res


def tess_number(image):
    """image -- PIL or Pillow image"""
    image = image.resize(tuple(x*2 for x in image.size), Image.BICUBIC)
    file = io.BytesIO()
    image.save(file, 'PNG')
    subp = subprocess.Popen(['tesseract', 'stdin', 'stdout','-psm=8', 'digits'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    res = subp.communicate(input=file.getvalue())
    print(res[0])
    return res[0].decode()


def tess_digit(image):
    """image -- PIL or Pillow image"""
    glyph_path = 'parsers/digit_glyphs'
    vals = []

    h1 = image.histogram()
    for file in os.listdir(glyph_path):
        h2 = Image.open(os.path.join(glyph_path, file)).histogram()
        rms = eqdist(h1, h2)
        vals.append((file[0], rms))
    val = min(vals, key=lambda x: x[1])
    return val[0]