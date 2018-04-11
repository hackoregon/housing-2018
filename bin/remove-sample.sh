#! /bin/bash

set -eou pipefail

if [ -f manage.py ]; then rm manage.py; fi
rm -rf dead_songs
rm -rf api

if [ -f ./Backups/dead_songs.sql ]; then rm ./Backups/dead_songs.sql; fi
