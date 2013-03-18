#!/bin/sh

KP=320

# python setup.py build_ext --inplace
python knapsack.py --price payload_final.txt --size no_version_disk_size_sql_with_dir.txt --wsize $(($KP*1024)) --fixsize > rsyncd-launch/${KP}g

# python update-rsync.py --src /srv/ftp-stage/pub/opensuse/ --srcalt /srv/ftp/pub/opensuse/ --dst 160g/ kp-sol-160.txt
