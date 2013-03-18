#!/bin/bash

HOST=mirror@pontifex2-opensuse

MB_HOST=149.44.161.13
MB_PASSWD=`cat mbpasswd`
MB_SQL="\"SELECT hash.size, to_timestamp(hash.mtime)::date, filearr.path
          FROM hash, filearr
          WHERE filearr.id=hash.file_id
             AND (filearr.path LIKE '%rpm' OR filearr.path LIKE '%.iso' or filearr.path LIKE '%.xml%')
             AND filearr.path NOT LIKE 'ensuse/%';\""

### AND filearr.path NOT LIKE 'repositories/home:%';\""

echo 'Getting the package list ...'
ssh $HOST "PGPASSWORD=$MB_PASSWD psql -U mb -h $MB_HOST -t -A -F ' ' mb_opensuse -c $MB_SQL" > disk_size_time_sql.txt

NDAYS=${1:-7}
SINCE=`date -d "$NDAYS days ago" +%Y-%m-%d`

# if [ -f last_time ]; then
#   SINCE=`cat last_time`
# else
#   SINCE=`date -d "1 week ago" +%Y-%m-%d`
# fi

echo 'Removing the date field and filtering the new packages ...'
python remove_time_filter_new.py --date $SINCE disk_size_time_sql.txt > disk_size_sql.txt 2> payload_new.txt
gzip -f disk_size_time_sql.txt

echo 'Removing version name ...'
python remove_package_version.py disk_size_sql.txt > no_version_disk_size_sql.txt
gzip -f disk_size_sql.txt

echo 'Adding directories sizes ...'
python disk_size_groups.py --size no_version_disk_size_sql.txt > no_version_disk_size_sql_with_dir.txt
gzip -f no_version_disk_size_sql.txt

date +%Y-%m-%d > last_time
