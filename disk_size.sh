#!/bin/bash

HOST=mirror@pontifex2-opensuse
PREFIX=/srv/ftp-stage/pub/opensuse

ssh $HOST "cd $PREFIX ; ( du --apparent-size . | sort -nr )" > disk_size.txt
