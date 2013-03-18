#!/bin/bash

PREFIX=/mounts/users-space/aplanas/knapsack
URL=http://langley.suse.de/pub/pontifex2-opensuse.suse.de/download.opensuse.org/
NPROCS=6


function process_day {
    year=$1; month=$2; day=$3

    log=$URL/$year/$month/download.opensuse.org-$year$month$day-access_log.gz
    touch $PREFIX/$year/$month/$year$month$day.txt
    if curl -sIf -o /dev/null "$log"; then
	mkdir -p $PREFIX/$year/$month
	curl -s "$log" | gunzip | python get_path.py | sort | uniq | cut -d ' ' -f 2- >$PREFIX/$year/$month/$year$month$day.txt
    fi
}


# If we don't say anything, we get the last 90 days
NDAYS=${1:-90}
LOGS=()

# Store the # on concurrent procs
count=0

for days_ago in `seq -w $NDAYS -1 0`; do
    # Get date in format YYYY-MM-DD and extract the components
    pdate=`date -d "$days_ago day ago" +%Y-%m-%d`
    year=`echo $pdate | cut -d'-' -f1`
    month=`echo $pdate | cut -d'-' -f2`
    day=`echo $pdate | cut -d'-' -f3`

    logfile=$PREFIX/$year/$month/$year$month$day.txt

    # If the size of the file is not zero, include the file and don't
    # call process_day()
    if [ -s $logfile ]; then
	LOGS+=($logfile)
	continue
    fi

    count=$((count + 1))
    ( process_day $year $month $day ) &

    LOGS+=($logfile)

    if [ $((count % $NPROCS)) -eq 0 ]; then
	wait
    fi
done

wait

sort --parallel=$NPROCS -T /var/tmp ${LOGS[*]} | uniq -c | sort --parallel=$NPROCS -T /var/tmp -nr > $PREFIX/_tmp_payload.txt
mv $PREFIX/_tmp_payload.txt $PREFIX/payload.txt
