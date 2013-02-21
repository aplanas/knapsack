#!/bin/bash

HOST=mirror@pontifex2-opensuse

MB_HOST=149.44.161.13
MB_PASSWD=`cat mbpasswd`
MB_SQL="\"SELECT hash.size, filearr.path
          FROM hash, filearr
          WHERE filearr.id=hash.file_id
             AND (filearr.path LIKE '%rpm' OR filearr.path LIKE '%.iso')
             AND filearr.path NOT LIKE 'ensuse/%';\""

### AND filearr.path NOT LIKE 'repositories/home:%';\""

echo 'Getting the package list ...'
ssh $HOST "PGPASSWORD=$MB_PASSWD psql -U mb -h $MB_HOST -t -A -F ' ' mb_opensuse -c $MB_SQL" > disk_size_sql.txt

echo 'Removing version name ...'
python remove_package_version.py disk_size_sql.txt > no_version_disk_size_sql.txt
gzip disk_size_sql.txt

echo 'Adding directories sizes ...'
python disk_size_groups.py --size no_version_disk_size_sql.txt > no_version_disk_size_sql_with_dir.txt
gzip no_version_disk_size_sql.txt
