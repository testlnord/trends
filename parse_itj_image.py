# -*- coding: utf-8 -*-
import os
import click
import logging

from PIL import Image
from dotenv import find_dotenv, load_dotenv

from core.crawlers.itj_crawler import ItjCrawler


@click.command()
@click.argument('image_name')
def main(image_name):

    with open(image_name, 'rb') as image_file:
        image = Image.open(image_file)
        itj_crawler = ItjCrawler()
        result = itj_crawler.parse_image(image)
        for date, value in result:
            print(date, value, sep=', ')
    pass


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # often useful for finding various files
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables

    main()
