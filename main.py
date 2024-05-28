import csv

import pendulum
from prettytable import PrettyTable

table = PrettyTable()
pendulum.set_local_timezone('Europe/Dublin')

csv_file = "C:\\Users\\CuppariA\\Downloads\\Billing period usage report-20-May-2024.csv"
date_range = []
time_intervals = []
usage_dict = dict({})
day_interval_first_half = (8, 17)
day_interval_second_half = (19, 23)
night_interval_first_half = (23, 0)
night_interval_second_half = (0, 8)
peak_interval = (17, 18)

day_rate = 25.67
night_rate = 16.65
peak_rate = 32.42


def is_day_usage(time: pendulum.DateTime):
    is_day_usage1 = [time.hour == t for t in range(day_interval_first_half[0], day_interval_first_half[1])]
    is_day_usage2 = [time.hour == t for t in range(day_interval_second_half[0], day_interval_second_half[1])]
    return any(is_day_usage1) or any(is_day_usage2)


def is_night_usage(time):
    night_usage1 = [time.hour == night_interval_first_half[0], time.hour == night_interval_first_half[1]]
    night_usage2 = [time.hour == t for t in range(night_interval_second_half[0], night_interval_second_half[1])]

    return any(night_usage1) or any(night_usage2)


def is_peak_usage(time):
    return any([time.hour == peak_interval[0], time.hour == peak_interval[1]])


day_usage = 0.0
night_usage = 0.0
peak_usage = 0.0

with open(csv_file, "r", newline='') as file:
    reader = list(csv.reader(file, delimiter=',', dialect='excel-tab'))
    date_range = reader[0][1:]
    time_intervals = reader[10][2:]
    for row in reader[11:]:
        if len(row) == 0 or row[1] == 'Usage Type':
            continue
        usage_day = row[1:]
        usage_dict.setdefault(usage_day[0], usage_day[1:])

table.field_names = ["Date", "Day Usage", "Night Usage", "Peak Usage", "Total for the day", "Day cost", "Night cost",
                     "Peak cost", "Total cost for the day"]
day_total = 0.0
night_total = 0.0
peak_total = 0.0
day_total_cost = 0.0
night_total_cost = 0.0
peak_total_cost = 0.0
for k, v in usage_dict.items():
    row_day = 0.0
    row_night = 0.0
    row_peak = 0.0

    for i in range(len(v)):
        kwh = v[i]
        if kwh == '':
            continue
        kwh = float(v[i])
        [day, month, year] = map(int, k.split('/'))
        [hour, minute] = map(int, time_intervals[i].split(':'))
        read_date = pendulum.datetime(year, month, day, hour, minute)
        if is_day_usage(read_date):
            day_total += kwh
            row_day += kwh
        elif is_night_usage(read_date):
            night_total += kwh
            row_night += kwh
        elif is_peak_usage(read_date):
            peak_total += kwh
            row_peak += kwh
    day_total_cost += (row_day * day_rate) / 100
    night_total_cost += (row_night * night_rate) / 100
    peak_total_cost += (row_peak * peak_rate) / 100
    table.add_row(
        [k, round(row_day, 3), round(row_night, 3), round(row_peak, 3), round(row_day + row_peak + row_night, 3),
         round((row_day * day_rate) / 100, 3),
         round((row_night * night_rate) / 100, 3),
         round((peak_rate * peak_total) / 100, 3),
         round((row_day * day_rate +
                row_night * night_rate +
                peak_rate * peak_total) / 100, 3)
         ])

table.add_row(["Total usage", round(day_total, 3), round(night_total, 3), round(peak_total, 3),
               round(day_total + night_total + peak_total, 3), round(day_total_cost,3), round(night_total_cost,3), round(peak_total_cost,3),
               round(day_total_cost + night_total_cost + peak_total_cost,3)])
print(table.get_string())
