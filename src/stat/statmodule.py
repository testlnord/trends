"""All stat functions and normalizations """
from numpy import median
import pandas
import rpy2.robjects


def sort_ts(series):
    # sorts ts by date
    return sorted(series, key=lambda x: x[1])

def outlierMAD(vals, k=10, t=3):
    """ Hampel filter

    Exports Hampel filter from R's pracma package. For more info see R documentation.
    :param vals: list of integers
    :param k: window length 2*k+1 in indices
    :param t: threshold, default is 3 (Pearson's rule).
    :return: list without outliers
    """
    if not outlierMAD.pracma:
        outlierMAD.pracma = True
        rpy2.robjects.r.library('pracma')  # load library before first usage
        
    df = rpy2.robjects.IntVector(vals)
    d = rpy2.robjects.r.hampel(df, k, t)
    return list(d[0])
outlierMAD.pracma = False


def outliers_filter(series):
    vals = [x for d, x in series]
    pred_z = 0
    for idx, v in enumerate(vals):
        if v > 1:
            pred_z = idx
            break
    vals = vals[pred_z:]
    try:
        vals = outlierMAD(vals)
        data = [(d, vals[idx - pred_z]) if idx > pred_z else (d, 0) for idx, (d, _) in enumerate(series)]
    except TypeError:
        data = series
    return data


def median_filter(series, k=3):
    vals = [x for d, x in series]
    pred_z = 0
    for idx, v in enumerate(vals):
        if v > 1:
            pred_z = idx
            break
    vals = vals[pred_z:]
    med = median(vals)
    mad = median([abs(x - med) for x in vals])
    vals = [x if med - k * mad < x < med + k * mad else None for x in vals]
    try:
        df = pandas.DataFrame([0] + vals)
        df = df.interpolate()
        vals = list(df[0])[1:]
        data = [(d, vals[idx - pred_z]) if idx > pred_z else (d, 0) for idx, (d, _) in enumerate(series)]
    except TypeError:
        data = series
    return data


def normalize_series(series):
    """ Normalize ts data
    :param series: raw ts data, list of (date, value) tuples
    :return: normalized data, list of (date, normalized value) tuples
    """
    data = [(x, y) for x, y in sorted(series, key=(lambda v: v[0]))]
    min_val = min(data, key=(lambda v: v[1]))[1]
    max_val = max(data, key=(lambda v: v[1]))[1]
    if max_val == min_val:
        return [(x, 0.5) for x, _ in data]
    return [(x, float(y - min_val)/(max_val - min_val)) for x, y in data]


def merge(series_list):
    # merges several ts into one series
    #todo write impl merge
    return series_list

def to_per_month_ts(series):
    """ Makes ts with per month frequency

    If frequency is higher then sums values
    :param series: time series with frequency higher or equal 1 month
    :return: monthly ts
    """
    #todo write impl per month
    return series


def prepare_data(raw_series_list):
    """ Prepares data for user
    :param raw_series_list: data from db
    :return: data for user
    """
    #todo write prepare data

if __name__ == "__main__":
    pass