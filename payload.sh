#!/bin/bash

PREFIX=/home/aplanas-suse/log
NPROCS=6


function process_month {
  year=$1; month=$2

  # Store the # on concurrent procs
  count=0
  for i in $PREFIX/$year/$month/*-access_log.gz ; do
    count=$((count + 1))
    python get_path.py $i > `mktemp $PREFIX/path-$year-$month-XXXXXXXXXX.txt` &
    if [[ $((count % $NPROCS)) -eq 0 ]]; then
      wait
    fi
  done
}

# Get the information from the last three months
process_month 2012 12
process_month 2013 01
process_month 2013 02

# sort --parallel=$NPROCS $PREFIX/path-*.txt -T $PREFIX | uniq -c | sort --parallel=$NPROCS -nr > $PREFIX/payload.txt
# gzip $PREFIX/path-*.txt
