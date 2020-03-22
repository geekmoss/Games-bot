from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit, fsolve
import io


def logistic_model(x, a, b, c): return c / (1 + np.exp(-(x - b) / a))


def exponential_model(x, a, b, c): return a * np.exp(b * (x - c))


def fit_logistic_model(x, y):
    fit = curve_fit(logistic_model, x, y, p0=[2, 70, 20000], maxfev=5000, bounds=([0.5, 30, 300], [10, 120, 7e+6]))

    (a, b, c) = (fit[0][0], fit[0][1], fit[0][2])
    # lastday when somebody is infected
    lastday = int(fsolve(lambda x: logistic_model(x, a, b, c) - int(c), b))

    errors = [np.sqrt(fit[1][i][i]) for i in [0, 1, 2]]
    return fit, lastday, errors, f"Parameters of logistic model fit\n - **a**: `{a}`\n - **b**: `{b}`\n - **c**: `{c}`\n - *errors of c:* `{errors[2]}`"


def fit_logistic_model_b(x, y, fixb):
    fit = curve_fit(logistic_model, x, y, p0=[2, fixb, 20000], bounds=[[1, fixb, 150], [10, fixb + 1, 10e+6]])

    a, b, c = fit[0][0], fit[0][1], fit[0][2]
    lastday = int(fsolve(lambda x: logistic_model(x, a, b, c) - int(c), b))
    errors = [np.sqrt(fit[1][i][i]) for i in [0, 1, 2]]
    return fit, lastday, errors, f"Parameters of logistic model fit\n - **a**: `{a}`\n - **b**: `{b}`\n - **c**: `{c}`\n - *errors of c:* `{errors[2]}`"


def fit_exponential_model(x, y):
    exp_fit = curve_fit(exponential_model, x, y, p0=[.02, .1, 2.8], maxfev=5000)
    return exp_fit


def plotchart(x, y, lastday, fit, exp_fit, errors):
    pred_x = list(range(max(x), lastday))
    plt.rcParams['figure.figsize'] = [7, 7]
    plt.rc('font', size=14)
    # Real data
    plt.scatter(x, y, label="Real data", color="red")
    # Predicted logistic curve
    plt.plot(x + pred_x, [logistic_model(i, fit[0][0], fit[0][1], fit[0][2]) for i in x + pred_x],
             label="Logistic model")
    # Predicted exponential curve
    plt.plot(x + pred_x, [exponential_model(i, exp_fit[0][0], exp_fit[0][1], exp_fit[0][2]) for i in x + pred_x],
             label="Exponential model")
    # line with predicted total infected
    plt.axhline(y=fit[0][2], color='b', linestyle='dotted')
    plt.text(lastday - 2, fit[0][2] * 1.02, int(fit[0][2]))
    # uncertainty interval +- errors
    plt.axhline(y=fit[0][2] - errors[2], color='lightblue', linestyle='dotted')
    plt.axhline(y=fit[0][2] + errors[2], color='lightblue', linestyle='dotted')
    plt.legend()
    plt.xlabel("Days since 1 January 2020")
    plt.ylabel("Total number of infected people")
    plt.ylim((min(y) * 0.9, fit[0][2] * 1.1))

    chart_io = io.BytesIO()
    plt.savefig(chart_io, format='png', bbox_inches='tight')
    chart_io.seek(0)
    plt.clf()

    return chart_io


def plotcharts_norm_vs_log(x, y, lastday, fit, exp_fit, errors, lastday2, fit2, errors2):
    pred_x = list(range(max(x), lastday))
    pred_x2 = list(range(max(x), lastday2))
    plt.rcParams['figure.figsize'] = [14, 7]
    plt.rc('font', size=10)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    # Real data
    ax1.scatter(x, y, label="Real data", color="red")
    # Predicted logistic curve
    ax1.plot(x + pred_x, [logistic_model(i, fit[0][0], fit[0][1], fit[0][2]) for i in x + pred_x],
             label="Optimistic logistic model b=" + str(int(fit[0][1])))
    ax1.plot(x + pred_x2, [logistic_model(i, fit2[0][0], fit2[0][1], fit2[0][2]) for i in x + pred_x2],
             label="Realistic logistic model b=" + str(int(fit2[0][1])))
    # Predicted exponential curve
    ax1.plot(x + pred_x, [exponential_model(i, exp_fit[0][0], exp_fit[0][1], exp_fit[0][2]) for i in x + pred_x],
             label="Exponential model")
    # line with predicted total infected
    ax1.axhline(y=fit[0][2], color='g', linestyle='dotted')
    ax1.text(lastday - 2, fit[0][2] * 1.02, int(fit[0][2]))
    ax1.axhline(y=fit2[0][2], color='b', linestyle='dotted')
    ax1.text(lastday2 - 2, fit2[0][2] * 1.02, int(fit2[0][2]))
    # uncertainty interval +- errors
    ax1.axhline(y=fit[0][2] - errors[2], color='lightblue', linestyle='dotted')
    ax1.axhline(y=fit[0][2] + errors[2], color='lightblue', linestyle='dotted')
    ax1.axhline(y=fit[0][2] - errors2[2], color='lightblue', linestyle='dotted')
    ax1.axhline(y=fit[0][2] + errors2[2], color='lightblue', linestyle='dotted')
    ax1.legend()
    ax1.set(xlabel="Days since 1 January 2020", ylabel="Total number of infected people",
            ylim=(min(y) * 0.9, max([fit[0][2], fit2[0][2]]) * 1.1))

    # Real data
    ax2.scatter(x, y, label="Real data", color="red")
    # Predicted logistic curve
    ax2.plot(x + pred_x, [logistic_model(i, fit[0][0], fit[0][1], fit[0][2]) for i in x + pred_x],
             label="Optimistic logistic model b=" + str(int(fit[0][1])))
    ax2.plot(x + pred_x2, [logistic_model(i, fit2[0][0], fit2[0][1], fit2[0][2]) for i in x + pred_x2],
             label="Realistic logistic model b=" + str(int(fit2[0][1])))
    # Predicted exponential curve
    ax2.plot(x + pred_x, [exponential_model(i, exp_fit[0][0], exp_fit[0][1], exp_fit[0][2]) for i in x + pred_x],
             label="Exponential model")
    # line with predicted total infected
    ax2.axhline(y=fit[0][2], color='g', linestyle='dotted')
    ax2.text(lastday - 2, fit[0][2] * 1.02, int(fit[0][2]))
    ax2.axhline(y=fit2[0][2], color='b', linestyle='dotted')
    ax2.text(lastday2 - 2, fit2[0][2] * 1.02, int(fit2[0][2]))
    # uncertainty interval +- errors
    ax2.axhline(y=fit[0][2] - errors[2], color='lightblue', linestyle='dotted')
    ax2.axhline(y=fit[0][2] + errors[2], color='lightblue', linestyle='dotted')
    ax2.axhline(y=fit[0][2] - errors2[2], color='lightblue', linestyle='dotted')
    ax2.axhline(y=fit[0][2] + errors2[2], color='lightblue', linestyle='dotted')
    ax2.legend()
    ax2.set(xlabel="Days since 1 January 2020", ylabel="Total number of infected people, log scale",
            ylim=(min(y) * 0.9, max([fit[0][2], fit2[0][2]]) * 1.1),
            yscale="log")

    chart_io = io.BytesIO()
    plt.savefig(chart_io, format='png', bbox_inches='tight')
    chart_io.seek(0)
    plt.clf()

    return chart_io


def analyze_data(df, estb=0):
    x = list(df.iloc[:, 0])
    y = list(df.iloc[:, 1])
    # try to fit all parameters a,b,c
    fit, lastday, errors, log_model_txt = fit_logistic_model(x, y)
    # try to fit parameters a,c,
    # estimate b (critical point) as e.g. 7-14 days after
    # quarantine and other actions were introduced in population
    fit_exp = fit_exponential_model(x, y)
    date_lastday = datetime(2020, 1, 1) + timedelta(days=lastday)
    log_model_txt_b = ""
    if estb > 0:
        fit2, lastday2, errors2, log_model_txt_b = fit_logistic_model_b(x, y, estb)
        chart = plotcharts_norm_vs_log(x, y, lastday, fit, fit_exp, errors, lastday2, fit2, errors2)
    else:
        chart = plotchart(x, y, lastday, fit, fit_exp, errors)

    return date_lastday, fit, errors, log_model_txt, log_model_txt_b, chart
