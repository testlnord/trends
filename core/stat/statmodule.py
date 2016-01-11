"""All stat functions and normalizations """
import datetime
from numpy import median
import pandas
from statsmodels.nonparametric.smoothers_lowess import lowess
from calendar import monthrange


def next_month(month):
    return datetime.date(month.year + (1 if month.month == 12 else 0 ), (month.month +1) if month.month < 12 else 1, 1)


def freq_month(series):
    result = {}
    for d, v in series:
        month = datetime.date(d.year, d.month, 1)
        if month not in result:
            result[month] = [0, monthrange(month.year, month.month)[1]]
        result[month][0] += v
    # fixing hanging ends
    # last month can have less measurements than overs
    max_day = max(series, key=lambda x: x[0])[0].date()
    cur_day = datetime.date.today()
    """:type : datetime.date"""
    max_month = datetime.date(max_day.year, max_day.month, 1)
    cur_month = datetime.date(cur_day.year, cur_day.month, 1)
    if cur_month == max_month:
        result[max_month][1] -= max_day.day - 1


    # adding missing months
    cur_m = min(result)
    """:type : datetime.date"""
    max_m = max(result)
    while cur_m < max_m:
        if cur_m not in result:
            result[cur_m] = (0,1)
        cur_m = next_month(cur_m)

    return ((d, pv[0]/pv[1]) for d, pv in result.items())


def continue_to_now(series):
    series = list(series)
    max_date = max(series, key=lambda x:x[0])[0]
    cur_month = datetime.date.today()
    cur_month = datetime.date(cur_month.year, cur_month.month, 1)
    max_date = next_month(max_date)
    while max_date < cur_month:
        series.append((max_date, 0))
        max_date = next_month(max_date)
    return series


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
