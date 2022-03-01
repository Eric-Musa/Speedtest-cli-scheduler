# import argparse
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as _date_parse
import numpy as np
import os
import pandas as pd
import pytz
import shutil

datetime_format = '%Y-%m-%d %H:%M:%S %Z'
date_format = '%Y-%m-%d'
today = datetime.today()
yesterday = today - timedelta(days=1)

today = datetime.strftime(today, date_format)
yesterday = datetime.strftime(yesterday, date_format)


print('today:', today)
print('yesterday:', yesterday)

csv_template = '%s.csv'

assert not os.path.isfile(csv_template % today) and os.path.isfile(csv_template % yesterday)
# Today's file should not exist yet but yesterday's should

header = [
    'Datestamp', 
    'Server ID', 
    'Sponsor', 
    'Server Name', 
    'Timestamp', 
    'Distance (km)', 
    'Ping (ms)', 
    'Download (Mbps)', 
    'Upload (Mbps)', 
    'Share', 
    'IP Address',
]
cols = [i for i, h in enumerate(header) if h != "Share"]
ydata = pd.read_csv(csv_template % yesterday, names=header, skiprows=1, usecols=cols)


def date_parse(date_str, format=None):
    format = format or datetime_format
    return _date_parse(date_str).astimezone(pytz.timezone('US/Eastern')).strftime(format)


ydata[['Download (Mbps)', 'Upload (Mbps)']] = ydata[['Download (Mbps)', 'Upload (Mbps)']].apply(lambda _: _*1e-6)
ydata['Timestamp'] = ydata['Timestamp'].apply(date_parse)

print(ydata)

shutil.move(csv_template % yesterday, os.path.join('archive', csv_template % yesterday))