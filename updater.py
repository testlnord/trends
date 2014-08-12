""" Updates data by schedule

simply calls source-specific updaters and then generate reports if data was changed
"""


from core.updaters.google import GoogleUpdater
from core.updaters.wiki import WikiUpdater


def update_data():
    wu = WikiUpdater()
    gu = GoogleUpdater()
    dirty = gu.update_data()
    return dirty

if __name__ == "__main__":
    print(update_data())