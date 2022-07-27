import bz2
from http import server
from statistics import pvariance
import numpy as np
import requests
from time import sleep
import datetime
import time
import pandas
import scipy.stats as sp
import matplotlib.pyplot as plt

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from scipy.stats import norm
from pyts.approximation import SymbolicAggregateApproximation
import math


class CompressionBasedDissimilarity(object):

    def __init__(self, n_letters=7):
        self.bins = None
        self.n_letters = n_letters

    def set_bins(self, bins):
        self.bins = bins

    def sax_bins(self, all_values):
        newList = [x for x in all_values if x > 0]
        bins = np.percentile(
            newList, np.linspace(0, 100, self.n_letters + 1)
        )
        bins[0] = 0
        bins[-1] = 1e1000
        return bins

    @staticmethod
    def sax_transform(all_values, bins):
        indices = np.digitize(all_values, bins) - 1
        alphabet = np.array([*("abcdefghijklmnopqrstuvwxyz"[:len(bins) - 1])])
        text = "".join(alphabet[indices])
        return str.encode(text)

    def calculate(self, m, n):
        if self.bins is None:
            m_bins = self.sax_bins(m)
            n_bins = self.sax_bins(n)
        else:
            m_bins = n_bins = self.bins
        m = self.sax_transform(m, m_bins)
        n = self.sax_transform(n, n_bins)
        len_m = len(bz2.compress(m))
        len_n = len(bz2.compress(n))
        len_combined = len(bz2.compress(m + n))
        return len_combined / (len_m + len_n)


# def getDataFromAPI(ip, chart, dimension, timeStepsBack=5):
#     points = timeStepsBack

#     r = requests.get(
#         'http://{}:19999/api/v1/data?chart={}&dim'
#         'ension={}&after=-{}&before=0&points={}&group=average&gtime=0&format=json&options=seconds&options'
#         '=jsonwrap'.format(ip, chart, dimension, timeStepsBack, points))

#     a = r.json()['result']['data']
#     last_metrics = []

#     for i in range(timeStepsBack):
#         last_metrics.append(a[i][1])

#     last_metrics.reverse()
#     return last_metrics


def calc_correlation(actual, predic):
    a_diff = actual - np.mean(actual)
    p_diff = predic - np.mean(predic)
    numerator = np.sum(a_diff * p_diff)
    denominator = np.sqrt(np.sum(a_diff ** 2)) * np.sqrt(np.sum(p_diff ** 2))
    #print(numerator, denominator)
    if math.isnan(numerator / denominator):
        return -2
    return numerator / denominator


# # print(server)
obj = CompressionBasedDissimilarity()


server = pandas.read_csv("server.csv", names=['row', 'timestamp', 'data'])

server.replace(0.0, 0.0001, inplace=True)

client = pandas.read_csv("client.csv", names=['row', 'timestamp', 'data'])

client.replace(0.0, 0.0001, inplace=True)

# print(server)

i = 0
result = []

while i < client.count()[0]-1:
    # server = getDataFromAPI("192.168.1.60", "system.cpu", "user", 15)

    # client = getDataFromAPI("192.168.1.61", "system.cpu", "user", 15)

    #print(server.data[i], client.data[i])

    # a = [server.data[i-2], server.data[i-1], server.data[i]]

    a = []

    for k in range(i, i+2):
        a.append(server.data[k])

    b = []

    for k in range(i, i+2):
        b.append(client.data[k])

    # b = [client.data[i-2], client.data[i-1], client.data[i]]

    #SAX print(obj.calculate(client, server))

    #print(datetime.datetime.fromtimestamp( server.timestamp[i]))
    #pearson correlation

    # result = calc_correlation(b, a)
    # print(result)
    # if result > 0.8:
    #     print("BUG-----------------", datetime.datetime.fromtimestamp(server.timestamp[i]))
    #     print("RESULT", result)
    #     print("SERVER", a, "CLIENT", b, "\n\n")

    #     print
    #     i+=45

    t_value, p_value = sp.ttest_ind(
        a, b)
    print(p_value, datetime.datetime.fromtimestamp(
        server.timestamp[i]), "\n ", a, b, "\n")

    alpha = 0.2

    if p_value > alpha:

        j = i

        j += 2

        a = []

        for k in range(j, j+2):
            a.append(server.data[k])

        b = []

        for k in range(j, j+2):
            b.append(client.data[k])

        t_value, p_value = sp.ttest_ind(
            a, b)
        if p_value > alpha:
            print("ANOMALY ", datetime.datetime.fromtimestamp(
                server.timestamp[i]))
            print("p_value = ", p_value)  # Debug
            print("SERVER", a, "CLIENT", b, "\n\n")

            i += 45

    i += 2

# # Parameters
# n_samples, n_timestamps = 5*60, 5*60

# # Toy dataset
# # rng = np.random.RandomState(41)
# # X = rng.randn(n_samples, n_timestamps)
# print(X)

# # SAX transformation
# n_bins = 4
# sax = SymbolicAggregateApproximation(n_bins=n_bins, strategy='uniform')
# X_sax = sax.fit_transform(X)

# # Compute gaussian bins
# bins = norm.ppf(np.linspace(0, 1, n_bins + 1)[1:-1])

# # Show the results for the first time series
# bottom_bool = np.r_[True, X_sax[0, 1:] > X_sax[0, :-1]]

# plt.figure(figsize=(6, 4))
# plt.plot(X[0], 'o--', label='Original')
# for x, y, s, bottom in zip(range(n_timestamps), X[0], X_sax[0], bottom_bool):
#     va = 'bottom' if bottom else 'top'
#     plt.text(x, y, s, ha='center', va=va, fontsize=14, color='#ff7f0e')
# plt.hlines(bins, 0, n_timestamps, color='g', linestyles='--', linewidth=0.5)
# sax_legend = mlines.Line2D([], [], color='#ff7f0e', marker='*',
#                            label='SAX - {0} bins'.format(n_bins))
# first_legend = plt.legend(handles=[sax_legend], fontsize=8, loc=(0.76, 0.86))
# ax = plt.gca().add_artist(first_legend)
# plt.legend(loc=(0.81, 0.93), fontsize=8)
# plt.xlabel('Time', fontsize=14)
# plt.title('Symbolic Aggregate approXimation', fontsize=16)
# plt.show()
