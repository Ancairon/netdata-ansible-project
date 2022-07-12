from asyncio.log import logger
from numpy import char
import numpy as np
import requests
import scipy.stats as sp
import time
from datetime import datetime

# This is a log file so I can have all the logged info in one place, but at the moment the output helps more for testing
logfile = open("log.txt", "a")

# A dictionary containing the valid metrics, the ones that are not anomalous. This will keep on growing as I find normal metrics
# In the future this might need to have a certain size and have rolling updates on the metrics so it doesn't consume a lot of memory
trained_metrics = {}

# TODO this is hardcoded for the two charts I am observing at the moment
trained_metrics.update({"system.cpu" + "user": []})
trained_metrics.update({"net.enp0s3" + "received": []})

# I assume that in last 30 seconds the machine was functioning at a normal state, so I gather that as my initial reference point of "normal" operation
r = requests.get(
    'http://localhost:19999/api/v1/data?chart={}&dim'
    'ension={}&after=-30&before=0&points=30&group=average&gtime=0&format=json&options=seconds&options'
    '=jsonwrap'.format("net.enp0s3", "received"))

a = r.json()['result']['data']

# TODO this could be using the function for appending to the trained model, but works for now
for i in range(len(a)):
    trained_metrics["net.enp0s3" + "received"].append(a[i][1])

#Netdata returns the data in reverse, newer->older, I want to have them older->newer for convenience
trained_metrics["net.enp0s3" + "received"].reverse()


def logToFile(line):

    logfile.write(" | " + line + "\n")


def anomalyMessage(chart, dimension, now):
    print("not equal, ANOMALY DETECTED on chart:", chart, "and dimension:",
          dimension)
    logToFile("not equal, ANOMALY DETECTED on chart: " + chart +
              " and dimension: " + dimension + ", Timestamp: " + now)


def appendToTrained(chart, dimension, metricsToExtend):
    trained_metrics[chart + dimension].extend(metricsToExtend)


# The function that is called for every chart, it has an interval of 1 second
def watch(chart, dimension):
    # I define the anomalies like a flag, so 0 means I don't have any anomalies, and 1 means that I have an anomaly
    anomalies = 0
    while (True):
        if (anomalies == 0):
            anomalies = watcher(chart, dimension)
            time.sleep(1)
        elif (anomalies == 1):
            anomalies = watcher(chart, dimension, True)
            time.sleep(1)


# This is the main function that does the statistic test
def watcher(chart, dimension, anomaly=False):
    # If there are no anomalies
    if (not anomaly):
        # Fetch the past 5 seconds of metrics
        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-5&before=0&points=5&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        a = r.json()['result']['data']
        last_metrics = []

        for i in range(3):
            last_metrics.append(a[i][1])

        last_metrics.reverse()

        # Do an independent T-test, on these latest metrics against the trained metrics
        t_value, p_value = sp.ttest_ind(trained_metrics[chart + dimension],
                                        last_metrics)

        alpha = 0.01
        print("p_value = ", p_value)  # Debug

        # If there is a significant difference in the two populations
        if p_value <= alpha:
            # Send an anomaly message and return 1 so the next loop runs with the state change logic
            anomalyMessage(chart, dimension, datetime.now().strftime("%c"))
            return +1

        # If there is no significant difference between the two populations, append the last 5 seconds to the trained model
        appendToTrained(chart, dimension, last_metrics)

        print("Length of trained metrics list = ",
              len(trained_metrics[chart + dimension]))  # Debug

    # Else if there was an anomaly before this examination of metrics, we need to 
    # make sure that the system is given some time to recover and we need to check for state changes
    else:
        print("Inspecting after anomaly, checking for state change.")

        # The system is given some time to recover from the anomaly
        time.sleep(90)

        # Gather the last 5 seconds of metrics
        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-5&before=0&points=5&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        a = r.json()['result']['data']
        last_metrics = []

        for i in range(3):
            last_metrics.append(a[i][1])

        last_metrics.reverse()

        # We need to check also for state changes, so we need the last 50 seconds (-5..-55) to also compare those to the last metrics
        # The state change would be the case where the system has recovered, but at another state
        # For example in a k8s cluster a pod has 70% usage before, then a more powerful pod replaces it, so we got 40% usage now, so we got a new "normal" state 
        metrics = []

        r = requests.get(
            'http://localhost:19999/api/v1/data?chart={}&dim'
            'ension={}&after=-55&before=-5&points=50&group=average&gtime=0&format=json&options=seconds&options'
            '=jsonwrap'.format(chart, dimension))

        b = r.json()['result']['data']

        for i in range(len(b)):
            metrics.append(b[i][1])

        metrics.reverse()

        # We run the two T-tests, against the last 50 seconds and against the trained model
        t_value, p_value = sp.ttest_ind(metrics, last_metrics)
        t_value, p_value_trained = sp.ttest_ind(
            trained_metrics[chart + dimension], last_metrics)

        print("p_value = ", p_value, "\ntrained p_value", p_value_trained) # Debug

        alpha = 0.01

        # If the latest metrics against the trained ones have significant differences
        if p_value_trained <= alpha:
            # Then we need to check the difference between the latest and the last 50 seconds (while we were waiting for recovery) 
            if p_value <= alpha:
                # If the last metrics had significant differences even from these metrics, then we have yet another anomaly. (this is unlikely to happen)
                anomalyMessage(chart, dimension, datetime.now().strftime("%c"))
                return +1
            # If the last 50 metrics don't have significant differences against the last metrics, then we have a state change, 
            # we flush the trained model and start from scratch again, adding both the metrics from the last 50 seconds, and the last metrics.
            # These are the trained metrics from now on 
            else:
                print("STATE CHANGE, changing the trained model")
                trained_metrics.update({chart + dimension: last_metrics})
                appendToTrained(chart, dimension, metrics)
        # If the latest metrics don't have significant differences against the trained model, then the system recovered successfully to the same state
        else:
            print("There is no state change, the system recovered, everything is normal again!")
            appendToTrained(chart, dimension, last_metrics)

    return 0

# In the current testing I am doing queries in a MySQL DB and observing the received bandwidth of the node
watch("net.enp0s3", "received")