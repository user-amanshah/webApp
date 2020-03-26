#!/bin/bash


#!/bin/bash



cd /home/ubuntu/webapp/


forever stop -a -e error.log -a  -l loger.log -c python3 views.py

sleep 2

sudo kill -9 `lsof -i:8080 -t`
sleep 2




#nohup python3 views.py >  /dev/null

forever start -a  -l loger.log -c python3 views.py

sleep 2

forever start -a  -l loger.log -c python3 views.py
#start cloudwatch####

cd ../.forever

pwd
sudo chmod 776 loger.log



sudo mv loger.log /opt/

cd

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/AmazonCloudWatch-config.json -s