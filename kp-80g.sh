#!/bin/sh

KP=80

# We need to reserve 21G for the repo and 16G for the ISOs 12.3

# python setup.py build_ext --inplace
python knapsack.py --price payload_final.txt --size no_version_disk_size_sql_with_dir.txt --wsize $(($KP*1024)) --fixsize > rsyncd-launch/${KP}g

# python update-rsync.py --src /srv/ftp/pub/opensuse --dst /srv/rsync-modules/160g kp-sol-123.txt
