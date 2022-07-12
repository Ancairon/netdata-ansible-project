# Module Imports
import random
import time
from time import sleep
import mariadb
import sys
import threading


def normalJob():
    #for i in range(0, 1):

    try:
        conn = mariadb.connect(user="root",
                               password="pass",
                               host="192.168.1.60",
                               port=3306,
                               database="employees")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        #continue
        return

    # Get Cursor
    cur = conn.cursor()

    cur.execute("SELECT first_name, last_name FROM employees")

    # for (first_name, last_name) in cur:
    #     print(f"First Name: {first_name}, Last Name: {last_name}")
    print("going fine")


def buggyJob():
    # for i in range(0, 5):

    try:
        conn = mariadb.connect(user="root",
                               password="pass",
                            #    wrong IP as a bug
                               host="192.168.1.61",
                               port=3306,
                               database="employees")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sleep(3)
    return


while(True):

    counter = 0
    k = 0

    timeSwitch = time.time() + 5 * 60

    while (time.time() <= timeSwitch):
        normalJob()

    print("Switching")

    for k in range(0, 200):
        print(timeSwitch/time.time())
        if (timeSwitch/time.time()==0):
            buggyJob()
            sleep(5)
            counter += 1
        else:
            normalJob()

    print("Bugged:", counter, "times")