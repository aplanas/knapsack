#!/bin/bash

# Prepare the KP data. The only pre-requisite is mirror_brain.txt
./prepare-kp.sh

# Compile with: python setup.py build_ext --inplace

for KP in 30 80 160 320 640 ; do
    python knapsack.py --price payload_final.txt --size no_version_disk_size_sql_with_dir.txt --wsize $(($KP*1024)) --fixsize > sort | rsyncd-launch/${KP}g
done

RSYNC_PASSWORD=Boopah5g rsync -avz rsyncd-launch/* knapsacks@pontifex2-opensuse.suse.de::put-knapsacks

git commit rsyncd-launch/* -m 'Automatic KP commit.'
git push -u origin master
