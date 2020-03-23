from datetime import date, datetime
from matplotlib.dates import datestr2num
import matplotlib.pyplot as plt
import Misc.CovidPrediction as cp
import pandas as pd
import numpy as np
import io


def __transform_data(data):
    return [{"infected": int(row["value"]), "date": datetime.strptime(row["date"][:10], "%Y-%m-%d").date()}
                      for row in data["totalPositiveTests"]]


def __get_pic(plot=None, fig=None) -> io.BytesIO:
    fig = fig if fig else plot.get_figure()
    chart_io = io.BytesIO()
    fig.savefig(chart_io, format='png', bbox_inches='tight')
    chart_io.seek(0)
    return chart_io


def infected(data) -> io.BytesIO:
    positive_tests = __transform_data(data)
    df = pd.DataFrame.from_dict(positive_tests)
    df.date = pd.to_datetime(df.date)
    df.set_index("date", inplace=True)

    fig, (ax1, ax2) = plt.subplots(2, 1)

    p = df.plot(figsize=(15, 10), ax=ax1)
    p.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="--")

    p2 = df.where(df.infected > 0).dropna().plot(figsize=(15, 10), ax=ax2)
    p2.set_yscale('log')
    p2.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="--")

    ax1b = ax1.twinx()
    df1b = df.pct_change().rename(columns={'infected': 'growth rate'}).dropna()
    p1b = df1b.plot(ax=ax1b, color="tab:green")
    ax1b.tick_params(axis='y', labelcolor="tab:green")

    vals = ax1b.get_yticks()
    ax1b.set_yticklabels(['{:.0%}'.format(x) for x in vals])

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()

    ax1.legend(lines1 + lines2, labels1 + labels2, loc=0)
    ax1b.get_legend().remove()

    f = __get_pic(fig=fig)
    return f


def by_region(data) -> io.BytesIO:
    df = pd.DataFrame.from_dict(data['infectedByRegion'])
    p = df.rename(columns={'value': 'infected', 'name': 'region'})\
        .plot(kind='bar', x='region', y='infected', figsize=(10, 5))
    p.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="--")

    for i in p.patches:
        p.text(i.get_x() + .1, i.get_height() + 4, str(i.get_height()), fontsize=8, color='dimgrey')
        pass

    f = __get_pic(p)
    return f


def quarantine_by_regions(data) -> io.BytesIO:
    df = pd.DataFrame.from_dict(data['regionQuarantine'][-1]['regionData'])
    p = df.rename(columns={'value': 'in quarantine', 'regionName': 'region'}) \
        .plot(kind='bar', x='region', y='in quarantine', figsize=(10, 5))
    p.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="--")

    for i in p.patches:
        p.text(i.get_x() + .1, i.get_height() + 4, str(i.get_height()), fontsize=8, color='dimgrey')
        pass

    f = __get_pic(p)
    return f


def demography(data) -> io.BytesIO:
    demo_by_age = {}
    for group in data['infectedByAgeSex']:
        for row in group['infectedByAge']:
            if demo_by_age.get(row['age'], False):
                demo_by_age[row['age']][group['sex']] = row['value']
                pass
            else:
                demo_by_age[row['age']] = {group['sex']: row['value']}
                pass
            pass
        pass

    demo_data = []
    for age in demo_by_age:
        demo_data.append({
            'age': age,
            'man': demo_by_age[age]['muž'],
            'woman': demo_by_age[age]['žena'],
        })
        pass

    df = pd.DataFrame.from_dict(demo_data)

    p = df.plot(kind='bar', y=['man', 'woman'], x='age')
    p.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="-")

    f = __get_pic(p)
    return f


def prediction(data, peak_day):
    start = date(2020, 1, 1)
    df = pd.DataFrame.from_dict(__transform_data(data))
    df['day'] = df['date'].map(lambda x: (x - start).days)

    df = df.reindex(columns=["day", "infected"])

    date_lastday, fit, errors, log_model_txt, log_model_txt_b, chart = cp.analyze_data(df, peak_day)
    return chart, {"last_date": date_lastday, "log_model_a": log_model_txt, "log_model_b": log_model_txt_b}
