"""Main K System """
import core.sources.sourcemanager as srsm
import core.stat.statmodule as statm

if __name__ == "__main__":
    sman = srsm.SourceManager()
    raw_data = sman.get_series('.net')
    print(raw_data)
    data = statm.prepare_data(raw_data)
    print(data)