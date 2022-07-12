from asyncio.log import logger
from numpy import char
import numpy as np
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
    'ension={}&after=-30&before=0&points=30&group=average&gtime=0&format=json&options=seconds&options'
    '=jsonwrap'.format("net.enp0s3", "received"))

a = r.json()['result']['data']

for i in range(len(a)):
    trained_metrics["net.enp0s3" + "received"].append(a[i][1])

trained_metrics["net.enp0s3" + "received"].reverse()


def anomalyMessage(chart, dimension, now):
    print("not equal, ANOMALY DETECTED on chart:", chart, "and dimension:",
          dimension)
    logToFile("not equal, ANOMALY DETECTED on chart: " + chart +
              " and dimension: " + dimension + ", Timestamp: " + now)
    #experiment
    #time.sleep(4)

def appendToTrained(chart, dimension, metricsToExtend):
    trained_metrics[chart + dimension].extend(metricsToExtend)

def watch(chart, dimension):
    anomalies = 0
    while (True):

        if (anomalies == 0):
            #anomalies = watch("system.cpu", "user") + watch("net.enp0s3", "received")
            anomalies = watcher(chart, dimension)
            time.sleep(1)
        elif (anomalies == 1):
            #anomalies = watch("system.cpu", "user", True) + watch("net.enp0s3", "received", True)
            anomalies = watcher(chart, dimension, True)
            time.sleep(1)

def watcher(chart, dimension, use_trained=False):

    if (not use_trained):
        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-5&before=0&points=5&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        a = r.json()['result']['data']
        last_metrics = []

        for i in range(3):
            last_metrics.append(a[i][1])

        last_metrics.reverse()

        # metrics = []

        # r = requests.get(
        #     'http://localhost:19999/api/v1/data?chart={}&dim'
        #     'ension={}&after=-15&before=-5&points=10&group=average&gtime=0&format=json&options=seconds&options'
        #     '=jsonwrap'.format(chart, dimension))

        # b = r.json()['result']['data']

        # for i in range(len(b)):
        #     metrics.append(b[i][1])

        # metrics.reverse()

        t_value, p_value = sp.ttest_ind(trained_metrics[chart + dimension], last_metrics)

        # print('Test statistic is %f' % float("{:.6f}".format(t_value)))

        # print('p-value is %f' % p_value)

        # alpha = 0.05
        alpha = 0.01

        print("p_value = ", p_value)
        if p_value <= alpha:
            anomalyMessage(chart, dimension, datetime.now().strftime("%c"))
            return +1

        appendToTrained(chart, dimension, last_metrics)
        print("Length of trained metrics list = ", len(trained_metrics[chart + dimension]))

    else:

        print("Inspecting after anomaly, checking for state change.")

        time.sleep(90)

        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-5&before=0&points=5&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        a = r.json()['result']['data']
        last_metrics = []

        for i in range(3):
            last_metrics.append(a[i][1])

        last_metrics.reverse()

        metrics = []

        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-55&before=-5&points=50&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        b = r.json()['result']['data']

        for i in range(len(b)):
            metrics.append(b[i][1])

        metrics.reverse()

       

        # trmr = np.asarray(trained_metrics[chart + dimension], dtype=object)
        # print("TRAINED METRICS", trained_metrics[chart + dimension])

        # print("LAST METRICS", last_metrics)
        t_value, p_value = sp.ttest_ind(metrics, last_metrics)
        t_value, p_value_trained = sp.ttest_ind(trained_metrics[chart + dimension], last_metrics)

        print("p_value = ", p_value, "\ntrained p_value", p_value_trained)
        # print('Test statistic is %f' % float("{:.6f}".format(t_value)))

        # print('p-value is %f' % p_value)

        # alpha = 0.05
        alpha = 0.01

        if p_value_trained <= alpha:
            if p_value <= alpha:
                anomalyMessage(chart, dimension, datetime.now().strftime("%c"))
                return +1
            else:
                print("STATE CHANGE, changing the trained model")
                trained_metrics.update({chart + dimension: last_metrics})
                appendToTrained(chart, dimension, metrics)               
        else:
            print("There is no state change, everything is normal again!")
            appendToTrained(chart, dimension, last_metrics)               

    return 0


#watch("system.cpu", "user")
# time.sleep(40)

watch("net.enp0s3", "received")