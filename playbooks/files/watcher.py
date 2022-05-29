from asyncio.log import logger
import requests
import scipy.stats as sp
import time
from datetime import datetime

logfile = open("log.txt", "a")
def logToFile(line):
    
    logfile.write(" | " + line + "\n")


trained_metrics = {}

trained_metrics.update({"system.cpu" + "user": []})
trained_metrics.update({"net.enp0s3" + "received": []})

r = requests.get(
    'http://localhost:19999/api/v1/data?chart={}&dim'
    'ension={}&after=-40&before=-10&points=30&group=average&gtime=0&format=json&options=seconds&options'
    '=jsonwrap'.format("net.enp0s3", "received"))

a = r.json()['result']['data']

for i in range(len(a)):
    trained_metrics["net.enp0s3" + "received"].append(a[i][1])

trained_metrics["net.enp0s3" + "received"].reverse()


def watch(chart, dimension, use_trained=False):
    r = requests.get(
        'http://localhost:19999/api/v1/data?chart={}&dim'
        'ension={}&after=-3&before=0&points=3&group=average&gtime=0&format=json&options=seconds&options'
        '=jsonwrap'.format(chart, dimension))

    a = r.json()['result']['data']
    last_metrics = []

    for i in range(3):
        last_metrics.append(a[i][1])

    last_metrics.reverse()

    metrics = []

    if (not use_trained):
        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-23&before=-3&points=20&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        b = r.json()['result']['data']

        for i in range(len(b)):
            metrics.append(b[i][1])

        metrics.reverse()
    else:

        metrics = trained_metrics[chart + dimension]

        print("USING TRAINED MODEL")

    t_value, p_value = sp.ttest_ind(metrics, last_metrics)

    # print('Test statistic is %f' % float("{:.6f}".format(t_value)))

    # print('p-value is %f' % p_value)

    # alpha = 0.05
    alpha = 0.1

    if p_value <= alpha:
        now = datetime.now().strftime("%c")
        print("not equal, ANOMALY DETECTED on chart:", chart, "and dimension:",
              dimension)
        logToFile("not equal, ANOMALY DETECTED on chart: " + chart +
                  " and dimension: " + dimension + ", Timestamp: " + now)
        #experiment
        time.sleep(4)
        return +1

    trained_metrics[chart + dimension] += metrics + last_metrics
    return 0

anomalies = 0

while (True):

    if (anomalies == 0):
        #anomalies = watch("system.cpu", "user") + watch("net.enp0s3", "received")
        anomalies = watch("net.enp0s3", "received")
        time.sleep(1)
    else:
        #anomalies = watch("system.cpu", "user", True) + watch("net.enp0s3", "received", True)
        anomalies = watch("net.enp0s3", "received", True)
        time.sleep(1)
