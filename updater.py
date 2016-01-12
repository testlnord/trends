""" Updates data by schedule

simply calls source-specific updaters and then generate reports if data was changed
"""
from core.config import init_logging
import logging

from core.updaters.google import GoogleUpdater
from core.updaters.wiki import WikiUpdater
from core.updaters.itj import ItjUpdater
from core.updaters.sot import SotUpdater
from core.updaters.gitstars import GitStarsUpdater
import core.stat.normalize as normalize



sources = [('google', GoogleUpdater, normalize.normalize_google),
           ('wiki', WikiUpdater, normalize.normalize_wiki),
           #('sousers', SoUsersUpdater, normalize.normalize_sousers),
           ('sot', SotUpdater, normalize.normalize_sot),
           ('itj', ItjUpdater, normalize.normalize_itj),
           ('gitstars', GitStarsUpdater, normalize.normalize_gitstars)]


def update_data_part(name, updater_class, norm_function):
    logger = logging.getLogger(__name__)
    logger.info("Updating %s data", name)
    upd = updater_class()
    if upd.update_data():
        logger.info("Data changed. Normalizing %s data", name)
        try:
            norm_function()
        except:
            logger.error("Normalization %s failed", name, exc_info=True)
        return True
    else:
        return False


# noinspection PyBroadException
def update_data():
    logger = logging.getLogger(__name__)

    dirty = False
    for name, upd_class, norm_fun in sources:
        try:
            dirty |= update_data_part(name, upd_class, norm_fun)
        except:  # need most common error here
            logger.error("Error occurred in processing %s source", name, exc_info=True)

    if dirty:
        logger.info("Data changed. Regenerate report2.")
        try:
            normalize.normalize()
        except:
            logger.error("Normalization failed.", exc_info=True)


if __name__ == "__main__":
    init_logging()
    update_data()


