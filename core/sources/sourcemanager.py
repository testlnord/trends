"""Main source manager module """

import os
from ..dbis import smdbi
from . import errors

class SourceManager:
    sources_classes = []

    def __init__(self):
        self.dbi = smdbi.SourmManagerDBI()
        # load sources in the end!
        self.sources = []
        for cls in self.sources_classes:
            self.sources.append(cls())

    def get_series(self, tech_name, start_date=None, end_date=None):
        tech = self.dbi.get_tech(tech_name)
        print(tech)
        if tech is None:
            self.dbi.add_tech(tech_name)
            for source in self.sources:  # todo make parallel
                source.add_tech(tech_name)

        result = []
        for source in self.sources:  # todo make this parallel too
            try:
                result.append(source.get_series(tech_name, start_date, end_date))
            except errors.UnknownTechnology:
                source.add_tech(tech_name)
                result.append(source.get_series(tech_name, start_date, end_date))
        return result


# Decorator for source managers
def source_decorator(cls):
    SourceManager.sources_classes.append(cls)
    return cls

# Load all sources
current_dir = os.path.dirname(os.path.abspath(__file__))
print(current_dir)
for file in os.listdir(current_dir):
    if file.endswith("_src.py"):
        with open(os.path.join(current_dir, file)) as src_script_file:
            exec(src_script_file.read())


if __name__ == "__main__":
    pass