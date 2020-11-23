import requests
import pandas
import time

import matplotlib.pyplot as plt

from datetime import datetime
from covid import Region


ab_codes = {
    "Calgary": 4832,
    "Central": 4833,
    "Edmonton": 4834,
    "North": 4835,
    "South": 4831
}


def get_date_list():
    # Generates correctly formatted list up until current day
    # Returns list of strings of dates
    dates = pandas.date_range(start="2020-02-01",end=datetime.today(), closed="left")
    dates = pandas.to_datetime(dates)
    date_list = []
    for date in dates:
        date_list.append(date.strftime("%d-%m-%Y"))
    return date_list


def generate_data(date_list, code_dict):
    # Generates data from calling API for each day
    for code in code_dict.values():
        print(code)
        cumulative = []
        days = []
        i = 0
        for date in date_list:
            i += 1
            print(f"Day {i}")
            info = Region(code, date)
            cumulative.append(info.cumulative_cases)
            days.append(i)
            time.sleep(0.1)
        plt.plot(days, cumulative, label=info.health_region.title())

    return

date_list = get_date_list()
generate_data(date_list, ab_codes)

plt.xlabel("Days")
plt.ylabel("Cumulative Cases")
plt.title("Covid in Alberta")
plt.show()