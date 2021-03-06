from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import pandas as pd
import shutil

datetime_format = '%Y-%m-%d %H:%M:%S %Z'
date_format = '%Y-%m-%d'

csv_template = '%s.csv'
png_template = os.path.join('aggregations', 'aggregate_%s.png')


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


def get_up_low_bounds(values, extend=0.5):
    mn, mx = values.min(), values.max()
    rad = (mx - mn)/2
    center = (mx + mn) / 2
    low = center - rad * (1 + extend)
    up = center + rad * (1 + extend)
    return [low, up]    


def main(today=None, yesterday=None, debug=True):
    today = today or datetime.today()
    today = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
    yesterday = yesterday or today - timedelta(days=1)

    today_str = datetime.strftime(today, date_format)
    yesterday_str = datetime.strftime(yesterday, date_format)

    if debug:
        print('today:', today_str)
        print('yesterday:', yesterday_str)
    
    assert debug or (not os.path.isfile(csv_template % today_str) and os.path.isfile(csv_template % yesterday_str))
    # Today's file should not exist yet but yesterday's should
    
    ydata = pd.read_csv(csv_template % yesterday_str, names=header, skiprows=1, usecols=cols).dropna()
    ydata[['Download (Mbps)', 'Upload (Mbps)']] = ydata[['Download (Mbps)', 'Upload (Mbps)']].apply(lambda _: _*1e-6)
    ydata['Datestamp'] = ydata['Datestamp'].apply(lambda _: datetime.fromtimestamp(_))
    print(ydata)

    if not debug:
        shutil.move(csv_template % yesterday_str, os.path.join('archive', csv_template % yesterday_str))

    datestamps = ydata['Datestamp'].values
    downloads = ydata['Download (Mbps)'].values
    uploads = ydata['Upload (Mbps)'].values

    fig, [ax1, ax2] = plt.subplots(2, 1)
    fig.suptitle('Download and Upload Speeds (Mbps) on %s' % yesterday_str)

    for ax in [ax1, ax2]:
        ax.set_xlim(yesterday, today)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %H:%M'))
        # Rotates and right-aligns the x labels so they don't crowd each other.
        for label in ax.get_xticklabels(which='major'):
            label.set(rotation=30, horizontalalignment='right')
    
    window = 10
    low_threshold = 100

    ax1.set_title('Downloads', loc='left', y=0.01, x=0.01, fontsize='small')
    up_low_bounds = get_up_low_bounds(downloads)
    ax1.plot(up_low_bounds, [low_threshold, low_threshold], color='black')
    ax1.set_ylim(up_low_bounds)
    download_mean, download_std = downloads.mean(), downloads.std()
    rolling_downloads = ydata['Download (Mbps)'].rolling(window=window).mean()
    rolling_download_stds = ydata['Download (Mbps)'].rolling(window=window).std()
    rolling_datestamps = ydata['Datestamp'][rolling_downloads.notna()]
    rolling_downloads = rolling_downloads.dropna()
    rolling_download_stds = rolling_download_stds.dropna()
    ax1.plot(rolling_datestamps, rolling_downloads + rolling_download_stds, color='green', alpha=0.3, label=str(int(download_mean+download_std)))
    ax1.plot(rolling_datestamps, rolling_downloads, color='blue', alpha=0.3, label=str(int(download_mean)))
    ax1.plot(rolling_datestamps, rolling_downloads - rolling_download_stds, color='red', alpha=0.3, label=str(int(download_mean-download_std)))
    ax1.plot(datestamps, downloads, color='black')
    ax1.legend(loc="upper left")
    
    
    # ax1.hlines(download_mean+download_std, yesterday, today, color="green", label=str(int(download_mean+download_std)))
    # ax1.hlines(download_mean, yesterday, today, color="black", label=str(int(download_mean)))
    # ax1.hlines(download_mean-download_std, yesterday, today, color="red", label=str(int(download_mean-download_std)))

    ax2.set_title('Uploads', loc='left', y=0.01, x=0.01, fontsize='small')
    up_low_bounds = get_up_low_bounds(uploads)
    ax2.plot(up_low_bounds, [low_threshold, low_threshold], color='black')
    ax2.set_ylim(up_low_bounds)
    upload_mean, upload_std = uploads.mean(), uploads.std()
    rolling_uploads = ydata['Upload (Mbps)'].rolling(window=window).mean()
    rolling_upload_stds = ydata['Upload (Mbps)'].rolling(window=window).std()
    rolling_datestamps = ydata['Datestamp'][rolling_uploads.notna()]
    rolling_uploads = rolling_uploads.dropna()
    rolling_upload_stds = rolling_upload_stds.dropna()
    ax2.plot(rolling_datestamps, rolling_uploads + rolling_upload_stds, color='green', alpha=0.3, label=str(int(upload_mean+upload_std)))
    ax2.plot(rolling_datestamps, rolling_uploads, color='blue', alpha=0.3, label=str(int(upload_mean)))
    ax2.plot(rolling_datestamps, rolling_uploads - rolling_upload_stds, color='red', alpha=0.3, label=str(int(upload_mean-upload_std)))
    ax2.plot(datestamps, uploads, color='black')
    ax2.legend(loc="upper left")
    # ax2.hlines(upload_mean+upload_std, yesterday, today, color="green", label=str(int(upload_mean+upload_std)))
    # ax2.hlines(upload_mean, yesterday, today, color="black", label=str(int(upload_mean)))
    # ax2.hlines(upload_mean-upload_std, yesterday, today, color="red", label=str(int(upload_mean-upload_std)))
    # fig.show()


    fig.tight_layout()
    if debug:
        fig.show()
    else:
        plt.savefig(png_template % yesterday)
        plt.close()
    
    return ydata

if __name__ == '__main__':
    main(debug=False)
