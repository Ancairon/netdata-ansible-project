# Module Imports
import random
from time import sleep
import mariadb
import sys
import threading


def normalJob():
    #for i in range(0, 1):

        try:
            conn = mariadb.connect(
                user="root",
                password="pass",
                host="192.168.1.60",
                port=3306,
                database="employees"

            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            #continue
            return

        # Get Cursor
        cur = conn.cursor()

        cur.execute(
            "SELECT first_name, last_name FROM employees")

        for (first_name, last_name) in cur:
            print(f"First Name: {first_name}, Last Name: {last_name}")


def buggyJob():
    # for i in range(0, 5):

    try:
        conn = mariadb.connect(
            user="root",
            password="pass",
            host="192.168.1.61",
            port=3306,
            database="employees"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    return

counter = 0

for k in range(0, 50):
    #random.randint(0, 30)
    if (k % 3 == 0) & k > 10:
        buggyJob()
        counter += 1
    else:
        normalJob()

print("Bugged:",counter, "times")