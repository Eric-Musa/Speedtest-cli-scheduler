#!/bin/sh
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate speedtest
datestamp=$(date '+%Y-%m-%d')
yesterday=$(date -v-1d '+%Y-%m-%d')
fname="$datestamp.csv"
yname="$yesterday.csv"

if [ -f $fname ]; then
    echo "running speedtest-cli and saving to $fname"
    echo $(date '+%s'),`speedtest-cli --csv` >> $fname
else
    if [ -f $yname ]; then  # only aggregate yesterday's data if first time running speedtest today
        echo "AGGREGATING DATA FROM YESTERDAY ($yesterday) <not really, not yet>"
        python aggregate.py
    fi
    echo "creating $fname and saving speedtest-cli data to it"
    echo $datestamp,`speedtest-cli --csv-header` >> $fname
    echo $(date '+%s'),`speedtest-cli --csv` >> $fname
fi
echo "finished"
