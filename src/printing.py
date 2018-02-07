__author__ = 'dutch_pool'


import datetime


def __print(message):
    time_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S: ")
    print(time_string + message)