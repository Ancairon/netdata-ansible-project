import datetime
import pandas
import scipy.stats as sp
import pickle

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

def calc_correlation(actual, predic):
    a_diff = actual - np.mean(actual)
    p_diff = predic - np.mean(predic)
    numerator = np.sum(a_diff * p_diff)
    denominator = np.sqrt(np.sum(a_diff ** 2)) * np.sqrt(np.sum(p_diff ** 2))
    # print(numerator, denominator)
    if math.isnan(numerator / denominator):
        return -2
    return numerator / denominator
"""

# text_file = open("bugs.dat", "r")
# lines = text_file.readlines()
# print( lines)
# print( len(lines))
# text_file.close()

# with open("bugs.dat", "rb") as fp:  # Unpickling
#     bugs = pickle.load(fp)


bugs = ['00:11:15', '00:14:43', '00:15:39', '00:19:50', '00:25:54', '00:34:09', '00:35:05', '00:44:45', '00:45:41',
        '00:46:38', '00:56:27', '01:01:26', '01:03:38', '01:08:19', '01:09:45', '01:17:16', '01:18:47', '01:20:50',
        '01:23:33', '01:31:39', '01:35:12', '01:39:00', '01:47:24', '01:49:53', '01:51:36', '01:57:26', '01:59:10',
        '02:02:57', '02:05:56', '02:07:47', '02:09:26', '02:11:15', '02:14:59', '02:20:52', '02:40:24', '02:48:06',
        '02:50:07', '02:54:03', '02:59:40', '03:00:37', '03:04:23', '03:08:39', '03:10:55', '03:14:33', '03:15:30',
        '03:19:21', '03:22:36', '03:23:32', '03:24:28', '03:26:12', '03:27:24', '03:35:19', '03:37:58', '03:39:41',
        '03:43:24', '03:44:20', '03:48:25', '03:56:42', '03:57:38', '03:59:41', '04:15:51', '04:18:05', '04:21:53',
        '04:31:38', '04:32:34', '04:34:54', '04:35:50', '04:36:46', '04:38:11', '04:40:00', '04:44:43', '04:45:39',
        '04:46:57', '04:50:50', '04:56:37', '05:08:49', '05:13:30', '05:16:00', '05:23:50', '05:25:35', '05:26:48',
        '05:32:36', '05:37:54', '05:39:56', '05:40:52', '05:42:55', '05:46:15', '05:50:13', '05:53:06', '06:07:21',
        '06:08:30', '06:09:27', '06:13:16', '06:21:32', '06:30:38', '06:40:59', '06:42:13', '06:45:03', '06:46:44',
        '06:50:10', '06:56:15', '07:01:13', '07:02:35', '07:04:18', '07:05:14', '07:07:02', '07:12:33', '07:21:23',
        '07:29:38', '07:32:27', '07:38:50', '07:40:50', '07:43:18', '07:55:42', '08:02:30', '08:04:47']
# 116 Bug array

# Get the timeseries from the csv files
server = pandas.read_csv("server.csv", names=['row', 'timestamp', 'data'])
client = pandas.read_csv("client.csv", names=['row', 'timestamp', 'data'])

i = 0
result = []
counter = 0

# Iterate the timeseries
while i < client.count()[0] - 1:

    # Make two dummy arrays to pass them into the test
    a = []
    for k in range(i, i + 2):
        a.append(server.data[k])

    b = []
    for k in range(i, i + 2):
        b.append(client.data[k])

    # Do a ttest against the two timeseries
    t_value, p_value = sp.ttest_ind(a, b)
    # We have a strict alpha (1-a = 99%)
    alpha = 0.050

    # If the two timeseries are similar we are going to check a few steps ahead and if we have again a similarity,
    # then we are clear to report an anomaly
    if p_value > alpha:
        # We seek some steps ahead
        j = i + 3
        # Dummy arrays
        try:
            a = []
            for k in range(j, j + 2):
                a.append(server.data[k])

            b = []
            for k in range(j, j + 2):
                b.append(client.data[k])
        except Exception as e:
            print(e)
            break
        # Do the test again
        t_value, p_value = sp.ttest_ind(a, b)
        # If we still have a similarity then we report the anomaly
        if p_value > alpha:
            try:
                # If the value in seconds found isn't near the real bug time, print a message, this is for debugging
                if not (datetime.datetime.fromtimestamp(server.timestamp[i - 10]).strftime("%H:%M:%S") < str(
                        bugs[counter]) < datetime.datetime.fromtimestamp(server.timestamp[i + 10]).strftime(
                    "%H:%M:%S")
                ):
                    print(i, "WRONG ANOMALY DETECTED")

                print("\n\nANOMALY ", datetime.datetime.fromtimestamp(server.timestamp[i + 1]).strftime("%H:%M:%S"),
                      "| Real bug timestamp -> ", bugs[counter])

                print("p_value = ", p_value)
                print("SERVER", a, "CLIENT", b, "\n\n")
            except Exception as e:
                print(e)

            # Bug counter
            counter += 1
            # Step of the recovery time
            i += 43
    i += 2

print("FOUND ", counter, " BUGS")
