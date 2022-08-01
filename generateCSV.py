from matplotlib.font_manager import json_dump
import pandas as pd
import requests


def getDataFromAPI(ip, chart, dimension, timeStepsBack=5):
    points = timeStepsBack

    r = requests.get(
        'http://{}:19999/api/v1/data?chart={}&dim'
        'ension={}&after=-{}&before={}&points={}&group=average&gtime=0&format=json&options=seconds&options'
        '=jsonwrap'.format(ip, chart, dimension, timeStepsBack, 0, points))

    a = r.json()['result']['data']
    a.reverse()

    return json_dump(a, "a.json")


getDataFromAPI("192.168.1.60", "system.cpu", "user", 12*60 * 60)

pdObj = pd.read_json("a.json")
pdObj.to_csv("server.csv")

getDataFromAPI("192.168.1.61", "system.cpu", "user", 12*60 * 60)

pdObj = pd.read_json("a.json")
pdObj.to_csv("client.csv")
