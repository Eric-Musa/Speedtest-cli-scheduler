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
cols = [i for i, h in enumerate(header) if h not in ["Timestamp", "Share"]]
ydata = pd.read_csv(csv_template % yesterday_str, names=header, skiprows=1, usecols=cols)

ydata[['Download (Mbps)', 'Upload (Mbps)']] = ydata[['Download (Mbps)', 'Upload (Mbps)']].apply(lambda _: _*1e-6)
ydata['Datestamp'] = ydata['Datestamp'].apply(lambda _: datetime.fromtimestamp(_))

print(ydata)

shutil.move(csv_template % yesterday_str, os.path.join('archive', csv_template % yesterday_str))


def get_up_low_bounds(values, extend=0.5):
    mn, mx = values.min(), values.max()
    rad = (mx - mn)/2
    center = (mx + mn) / 2
    low = center - rad * (1 + extend)
    up = center + rad * (1 + extend)
    return [low, up]


datestamps = ydata['Datestamp'].values
downloads = ydata['Download (Mbps)'].values
uploads = ydata['Upload (Mbps)'].values

fig, [ax1, ax2] = plt.subplots(2, 1)

fig.suptitle('Download and Upload Speeds (Mbps) on %s' % today_str)

ax1.set_title('Downloads', loc='left', y=0.01, x=0.01, fontsize='small')
ax1.plot(datestamps, downloads)
ax1.set_ylim(get_up_low_bounds(downloads))
download_mean, download_std = downloads.mean(), downloads.std()
ax1.hlines(download_mean+download_std, yesterday, today, color="green", label=str(int(download_mean+download_std)))
ax1.hlines(download_mean, yesterday, today, color="black", label=str(int(download_mean)))
ax1.hlines(download_mean-download_std, yesterday, today, color="red", label=str(int(download_mean-download_std)))
ax1.legend(loc="upper left")

ax2.set_title('Uploads', loc='left', y=0.01, x=0.01, fontsize='small')
ax2.plot(datestamps, uploads)
ax2.set_ylim(get_up_low_bounds(uploads))
upload_mean, upload_std = uploads.mean(), uploads.std()
ax2.hlines(upload_mean+upload_std, yesterday, today, color="green", label=str(int(upload_mean+upload_std)))
ax2.hlines(upload_mean, yesterday, today, color="black", label=str(int(upload_mean)))
ax2.hlines(upload_mean-upload_std, yesterday, today, color="red", label=str(int(upload_mean-upload_std)))
ax2.legend(loc="upper left")
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
