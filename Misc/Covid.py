from datetime import date, datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io


ax = plt.gca()
plt.tight_layout(3.5)


def __transform_data(data):
    return [{"infected": int(row["value"]), "date": datetime.strptime(row["date"][:10], "%Y-%m-%d").date()}
                      for row in data["totalPositiveTests"]]


def infected(data) -> io.BytesIO:
    positive_tests = __transform_data(data)
    df = pd.DataFrame.from_dict(positive_tests)
    df.date = pd.to_datetime(df.date)
    df.set_index("date", inplace=True)

    p = df.plot(ax=ax)
    p.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="-")

    chart_io = io.BytesIO()
    p.get_figure().savefig(chart_io, format='png')
    plt.cla()
    chart_io.seek(0)
    return chart_io


def infected_log(data) -> io.BytesIO:
    positive_tests = __transform_data(data)
    df = pd.DataFrame.from_dict(positive_tests)
    df.date = pd.to_datetime(df.date)
    df.set_index("date", inplace=True)

    p = df.plot(ax=ax)
    p.set_yscale('log')
    p.grid(color="black", alpha=.5, axis="y", which="both", linewidth=0.5, linestyle="-")

    chart_io = io.BytesIO()
    p.get_figure().savefig(chart_io, format='png')
    plt.cla()
    chart_io.seek(0)
    return chart_io
