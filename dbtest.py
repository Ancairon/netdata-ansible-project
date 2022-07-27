# Module Imports
import random
import time
from time import sleep
import tqdm
from tokenize import endpats
# import mysql
import MySQLdb as mysql


def normalJob(seed):
    work()
    #for i in range(0, 1):
    try:
        conn = mysql.connect(user="root",
                             password="pass",
                             host="192.168.1.60",
                             port=3306,
                             database="employees")
    except mysql.Error as e:
        print(f"Error connecting to mysql Platform: {e}")
        #continue
        return

    # Get Cursor
    cur = conn.cursor()

    match seed:
        case 0:
            cur.execute(
                "SELECT * FROM employees WHERE first_name LIKE '__R%';")
        case 1:
            cur.execute("select * from employees where gender = 'M';")
        case 2:
            cur.execute("select * from employees where gender = 'F';")
        case 3:
            cur.execute(
                "select * from employees where birth_date > 1971-08-10;")
        case 4:
            cur.execute(
                "select * from employees where birth_date > 1971-08-10 and hire_date < 1995-05-05;")
        case 5:
            cur.execute(
                "select e.first_name, e.birth_date from employees e JOIN employees b on e.emp_no = b.emp_no where e.first_name like 'B%';")
        case 6:
            cur.execute(
                "select e.first_name, e.birth_date from employees e JOIN employees b on e.emp_no = b.emp_no;")
        case 7:
            cur.execute(
                "select first_name from employees where first_name like 'Bo%'")
        case 8:
            cur.execute(
                "select last_name, emp_no from employees  where emp_no % 3 = 0;")
        case 9:
            cur.execute(
                "select * from employees where last_name like '%"+"a"+"%';")

    # for (first_name, last_name) in cur:
    #     print(f"First Name: {first_name}, Last Name: {last_name}")
    print("going fine")


def buggyJob(seed=2):
    # for i in range(0, 5):
    work()
    match seed:
        case 0:
            try:
                conn = mysql.connect(user="root",
                                     password="pass",
                                     #    wrong IP as a bug
                                     host="192.168.1.61",
                                     port=3306,
                                     database="employees")
            except mysql.Error as e:
                print(f"ERROR!: {e}")
                sleep(3)
            return
        case 1:
            try:
                conn = mysql.connect(user="root",
                                     password="pass",
                                     host="192.168.1.60",
                                     port=3306,
                                     database="employees")

                # Get Cursor
                cur = conn.cursor()

                cur.execute("SELECT first_name, last_name FROM wrongtable")
            except mysql.Error as e:
                print(f"ERROR!: {e}")
                sleep(3)
        case 2:
            try:
                conn = mysql.connect(user="root",
                                     password="pass",
                                     host="192.168.1.60",
                                     port=3306,
                                     database="employees")

                # Get Cursor
                cur = conn.cursor()

                cur.execute("SELECT first_name, wrongcolumn FROM employees")
            except mysql.Error as e:
                print(f"ERROR!: {e}")
                sleep(3)
        case 3:
            try:
                conn = mysql.connect(user="root",
                                     password="pass",
                                     host="192.168.1.60",
                                     port=3306,
                                     database="employees")

                # Get Cursor
                cur = conn.cursor()

                cur.execute("SELECT * FROM employees where")
            except mysql.Error as e:
                print(f"ERROR!: {e}")
                sleep(3)


def work():
    dummy = 0
    print("WORKING...")
    for i in tqdm.tqdm(range(0, 5000000)):
        dummy = dummy * 5
    print("Done working, querying now...")


endTime = time.time() + 5 * 60

counter = 0

timestamps = []

while(time.time() != endTime):

    timeSwitch = time.time() + 30

    while (time.time() <= timeSwitch):

        normalJob(random.randint(0, 9))

    print("Switching")

    for k in range(0, 200):
        if (random.randint(0, 10) == 5):

            timestamps.append(time.strftime("%H:%M:%S", time.localtime()))
            print(timestamps)
            buggyJob(random.randint(0, 3))
            sleep(40)
            counter += 1
        else:
            normalJob(random.randint(0, 9))

print("Bugged:", counter, "times")
