# import argparse
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse as _date_parse
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pytz
import shutil

datetime_format = '%Y-%m-%d %H:%M:%S %Z'
date_format = '%Y-%m-%d'
today = datetime.today()
yesterday = today - timedelta(days=1)

today_str = datetime.strftime(today, date_format)
yesterday_str = datetime.strftime(yesterday, date_format)


print('today:', today_str)
print('yesterday:', yesterday_str)

csv_template = '%s.csv'
png_template = os.path.join('aggregations', 'aggregate_%s.png')

assert not os.path.isfile(csv_template % today_str) and os.path.isfile(csv_template % yesterday_str)
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
ydata = pd.read_csv(csv_template % yesterday_str, names=header, skiprows=1, usecols=cols)


def date_parse(date_str, format=None):
    format = format or datetime_format
    return _date_parse(date_str).astimezone(pytz.timezone('US/Eastern'))  # .strftime(format)


ydata[['Download (Mbps)', 'Upload (Mbps)']] = ydata[['Download (Mbps)', 'Upload (Mbps)']].apply(lambda _: _*1e-6)
ydata['Timestamp'] = ydata['Timestamp'].apply(date_parse)

print(ydata)

shutil.move(csv_template % yesterday, os.path.join('archive', csv_template % yesterday))


def get_up_low_bounds(values, extend=0.5):
    mn, mx = values.min(), values.max()
    rad = (mx - mn)/2
    center = (mx + mn) / 2
    low = center - rad * (1 + extend)
    up = center + rad * (1 + extend)
    return [up, low]


timestamps = ydata['Timestamp'].values
downloads = ydata['Download (Mbps)'].values
uploads = ydata['Upload (Mbps)'].values

fig, [ax1, ax2] = plt.subplots(2, 1)

fig.suptitle('Download and Upload Speeds (Mbps) on %s' % today_str)

ax1.set_title('Downloads', loc='left', y=0.01, x=0.01, fontsize='small')
ax1.plot(timestamps, downloads)
ax1.set_ylim(get_up_low_bounds(downloads))

ax2.set_title('Uploads', loc='left', y=0.01, x=0.01, fontsize='small')
ax2.plot(timestamps, uploads)
ax2.set_ylim(get_up_low_bounds(uploads))
# fig.show()

import matplotlib.dates as mdates

for ax in [ax1, ax2]:
    ax.set_xlim(yesterday, today)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # Rotates and right-aligns the x labels so they don't crowd each other.
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=30, horizontalalignment='right')

fig.tight_layout()
# fig.show()
plt.savefig(png_template % yesterday)
plt.close()
