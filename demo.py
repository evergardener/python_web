import datetime
import time

import pytz as pytz


def main():
    time1 = time.time()
    test_write_latest(time1)

def test_timestamp():
    time_stamp = time.time()
    # print(time_stamp)
    date_array = datetime.datetime.fromtimestamp(time_stamp)
    format_time = date_array.strftime("%Y-%m-%d %H:%M:%S")

    time_stamp2 = time.time()
    date_array2 = datetime.datetime.utcfromtimestamp(time_stamp2)
    format_time2 = date_array.strftime("%Y-%m-%d %H:%M:%S")
    print(format_time)
    print(format_time2)
    print(format_time == format_time2)

def test_read_file():
    with open('test.txt', 'r') as f:
        print(f.readline())
        print(f.readline())
        f.close()

def test_write_file(num):
    with open('test.txt', 'w') as f:
        f.write(num)

def test_write_latest(data):
    with open('test.txt', 'w+') as f:
        ori = f.readline()
        if ori < str(data):
            f.write(str(data))
    f.close()

if __name__ == '__main__':
    main()