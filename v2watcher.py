import bz2
import numpy as np
import datetime
import pandas
import scipy.stats as sp
import math

"""tests
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
"""


def calc_correlation(actual, predic):
    a_diff = actual - np.mean(actual)
    p_diff = predic - np.mean(predic)
    numerator = np.sum(a_diff * p_diff)
    denominator = np.sqrt(np.sum(a_diff ** 2)) * np.sqrt(np.sum(p_diff ** 2))
    # print(numerator, denominator)
    if math.isnan(numerator / denominator):
        return -2
    return numerator / denominator


server = pandas.read_csv("server.csv", names=['row', 'timestamp', 'data'])
client = pandas.read_csv("client.csv", names=['row', 'timestamp', 'data'])

i = 0
result = []
counter = 0

while i < client.count()[0] - 1:
    a = []
    for k in range(i, i + 2):
        a.append(server.data[k])

    b = []
    for k in range(i, i + 2):
        b.append(client.data[k])

    t_value, p_value = sp.ttest_ind(a, b)

    alpha = 0.01

    if p_value > alpha:
        j = i + 4

        a = []
        for k in range(j, j + 2):
            a.append(server.data[k])

        b = []
        for k in range(j, j + 2):
            b.append(client.data[k])

        t_value, p_value = sp.ttest_ind(a, b)
        if p_value > alpha:
            print("\n\nANOMALY ",
                  datetime.datetime.fromtimestamp(server.timestamp[i + 1]))
            print("p_value = ", p_value)
            print("SERVER", a, "CLIENT", b, "\n\n")
            counter += 1
            i += 45
    i += 2

print("FOUND ", counter, " BUGS")
