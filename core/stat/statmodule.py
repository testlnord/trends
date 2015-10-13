"""All stat functions and normalizations """
import datetime
from numpy import median
import pandas
from statsmodels.nonparametric.smoothers_lowess import lowess


def freq_month(series, month_average=True):
    result = {}
    for d, v in series:
        month = datetime.date(d.year, d.month, 1)
        if month not in result:
            result[month] = [0, 0]
        result[month][0] += v
        result[month][1] += 1
    if month_average:
        return ((d, pv[0]/pv[1]) for d, pv in result.items())
    else:
        return ((d, pv[0]) for d, pv in result.items())


def sort_ts(series):
    # sorts ts by date
    return sorted(series, key=lambda x: x[0])


def hampel(vals, k, t=3):
    """ Hampel filter

    Exports Hampel filter from R's pracma package. For more info see R documentation.
    :param vals: list of integers
    :param k: window length 2*k+1 in indices
    :param t: threshold, default is 3 (Pearson's rule).
    :return: list without outliers
    """

    n = len(vals)
    y = vals
    ind = []
    L = 1.4826  # expectation of 1.4826 times the MAD for large samples of normally distributed Xi
                # is approximately equal to the population standard deviation
    for i in range(k + 1, n - k):
        vals0 = median(vals[i - k:i + k])
        S0 = L * median([abs(v - vals0) for v in vals[i - k:i + k]])
        if abs(vals[i] - vals0) > t * S0:
            y[i] = vals0
            ind.append(i)

    return y, ind


def outliers_filter(series):
    vals = [x for d, x in series]
    pred_z = 0
    for idx, v in enumerate(vals):
        if v > 1:
            pred_z = idx
            break
    vals = vals[pred_z:]
    try:
        vals, _ = hampel(vals)
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
        return [(x, 0) for x, _ in data]
    return [(x, float(y - min_val) / (max_val - min_val)) for x, y in data]


def divergence(series):
    result_series = []
    prev = None
    for d, v in series:
        if prev is None:
            prev = v
            result_series.append((d, 0))
        else:
            result_series.append((d, v - prev))
            prev = v
    return result_series
