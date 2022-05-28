import requests
import scipy.stats as sp
import time
from datetime import datetime


def logToFile(line):
    logfile  = open("log.txt", "a")
    logfile.write("{line}\n\n")

def watch(chart, dimension):
    r = requests.get(
        'http://localhost:19999/api/v1/data?chart={}&dim'
        'ension={}&after=-3&before=0&points=3&group=average&gtime=0&format=json&options=seconds&options'
        '=jsonwrap'.format(chart, dimension))

    a = r.json()['result']['data']
    last_metrics = []

    for i in range(3):
        last_metrics.append(a[i][1])

    last_metrics.reverse()

    r = requests.get(
        'http://localhost:19999/api/v1/data?chart={}&dim'
        'ension={}&after=-23&before=-3&points=20&group=average&gtime=0&format=json&options=seconds&options'
        '=jsonwrap'.format(chart, dimension))

    b = r.json()['result']['data']
    metrics = []

    for i in range(20):
        metrics.append(b[i][1])

    metrics.reverse()

    t_value, p_value = sp.ttest_ind(metrics, last_metrics)

    # print('Test statistic is %f' % float("{:.6f}".format(t_value)))

    # print('p-value is %f' % p_value)

    # alpha = 0.05
    alpha = 0.10

    if p_value <= alpha:
        now = datetime.now().strftime("%c")
        print("not equal, ANOMALY DETECTED on chart:", chart, "and dimension:", dimension)
        logToFile("not equal, ANOMALY DETECTED on chart: {chart} and dimension: {dimension}, Timestamp: {now}")
        
    #else:
        #print("no significant difference on chart:", chart, "and dimension:", dimension)
        #logToFile("no significant difference on chart: {chart} and dimension: {dimension}")


while(True):
    watch("system.cpu", "user")

    # laptop watch("net.wlp1s0", "received")

    watch("net.enp0s3", "received")
    time.sleep(1)
