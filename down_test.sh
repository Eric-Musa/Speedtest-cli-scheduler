#!/bin/zsh

conda activate speedtest
datestamp=$(date '+%Y-%m-%d')
fname="$datestamp.csv"
echo $datestamp,`speedtest-cli --csv-header` >> $fname
echo $(date '+%s'),`speedtest-cli --csv` >> $fname