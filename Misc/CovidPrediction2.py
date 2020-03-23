from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit, fsolve


def logistic_model(x, a, b, c): return c / (1 + np.exp(-(x - b) / a))


def exponential_model(x, a, b, c): return a * np.exp(b * (x - c))


def fit_exponential_model(x, y):
    exp_fit = curve_fit(exponential_model, x, y, p0=[1, 1, 1])
    return exp_fit


def fit_logistic_model(x, y):
    fit = curve_fit(logistic_model, x, y, p0=[2, 100, 2000])
    errors = [np.sqrt(fit[1][i][i]) for i in [0, 1, 2]]
    return fit, errors


def analyze_data(df):
    x = list(df.iloc[:, 0])
    y = list(df.iloc[:, 1])

    fit, errors = fit_logistic_model(x ,y)
    exp_fit = fit_exponential_model(x, y)

    a, b, c = fit[0][0], fit[0][1], fit[0][2]
    sol = int(fsolve(lambda x: logistic_model(x, a, b, c) - int(c), b))
    pred_x = list(range(int(max(x)), int(sol)))
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
    plt.legend()
    plt.xlabel("Days since 1 January 2020")
    plt.ylabel("Total number of infected people")
    plt.ylim((min(y) * 0.9, c * 1.1))
    plt.show()