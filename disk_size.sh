#!/bin/bash

NDAYS=${1:-7}
SINCE=`date -d "$NDAYS days ago" +%Y-%m-%d`

if [ -f mirror_brain.txt ] ; then
    echo 'Removing the date field and filtering the new packages ...'
    python remove_time_filter_new.py --date $SINCE mirror_brain.txt > disk_size_sql.txt 2> payload_new.txt
    gzip -f mirror_brain.txt

    echo 'Removing version name ...'
    python remove_package_version.py disk_size_sql.txt > no_version_disk_size_sql.txt
    gzip -f disk_size_sql.txt

    echo 'Removing version name in payload_new ...'
    python remove_package_version.py payload.txt > no_version_disk_size_sql.txt
    gzip -f disk_size_sql.txt

    echo 'Adding directories sizes ...'
    python disk_size_groups.py --size no_version_disk_size_sql.txt > no_version_disk_size_sql_with_dir.txt
    gzip -f no_version_disk_size_sql.txt
fi
