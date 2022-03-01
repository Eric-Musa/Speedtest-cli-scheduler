#!/bin/zsh
source activate speedtest
datestamp=$(date '+%Y-%m-%d')
yesterday=$(date -v-1d '+%Y-%m-%d')
fname="$datestamp.csv"
yname="$yesterday.csv"

if [ -f $fname ]; then
    if [ -f $yname ]; then
        echo "AGGREGATING DATA FROM YESTERDAY ($yesterday) <not really, not yet>"
    fi
    echo "running speedtest-cli and saving to $fname"
    echo $(date '+%s'),`speedtest-cli --csv` >> $fname
else
    echo "creating $fname and saving speedtest-cli data to it"
    echo $datestamp,`speedtest-cli --csv-header` >> $fname
    echo $(date '+%s'),`speedtest-cli --csv` >> $fname
fi
echo "finished"
