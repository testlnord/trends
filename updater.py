""" Updates data by schedule

simply calls source-specific updaters and then generate reports if data was changed
"""
import logging

from core.updaters.google import GoogleUpdater
from core.updaters.wiki import WikiUpdater
from core.updaters.itj import ItjUpdater
from core.updaters.sot import SotUpdater
from core.updaters.sousers import SoUsersUpdater
import core.stat.normalize as normalize


def update_data():
    logger = logging.getLogger(__name__)

    dirty = False


    logger.info("Updating google data")
    try:
        gu = GoogleUpdater()
        if gu.update_data():
            logger.info("Normalizing google data")
            normalize.normalize_google()
            dirty = True
        logger.info("Finish google data")
    except:  # need most common error here
        logger.warning("Error occurred.", exc_info=True)

    logger.info("Updating wiki data")
    try:
        wu = WikiUpdater()
        if wu.update_data():
            logger.info("Normalizing wiki data")
            normalize.normalize_wiki()
            dirty = True
        logger.info("Finish wiki data")
    except:
        logger.warning("Error occurred.", exc_info=True)

    logger.info("Updating itj data")
    try:
        iu = ItjUpdater()
        if iu.update_data():
            logger.info("Normalizing itj data")
            normalize.normalize_itj()
            dirty = True
        logger.info("Finish itj data")
    except:
        logger.warning("Error occurred.", exc_info=True)

    logger.info("Updating SO data")
    try:
        su = SotUpdater()
        if su.update_data():
            logger.info("Normalize SO data")
            normalize.normalize_sot()
            dirty = True
        logger.info("Finish SO data")
    except:
        logger.warning("Error occurred.", exc_info=True)

    try:
        logger.info("Updating SO users data")
        suu = SoUsersUpdater()
        if suu.update_data():
            logger.info("Normalize SO users data")
            normalize.normalize_sousers()
            dirty = True
        logger.info("Finish SO users data")
    except:
        logger.warning("Error occurred.", exc_info=True)

    if dirty:
        logger.info("Data changed. Regenerate report2.")
        try:
            normalize.normalize()
        except:
            logger.warning("Normalization failed.", exc_info=True)


if __name__ == "__main__":
    update_data()
