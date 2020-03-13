#!/bin/bash


#!/bin/bash



cd /home/ubuntu/webapp/

sudo kill -9 `lsof -i:8080 -t`

#nohup python3 views.py >  /dev/null

forever start -c python3 views.py
