#!/bin/bash


#!/bin/bash



cd /home/ubuntu/webapp/

sudo kill -9 `lsof -i:8080 -t`

forever stop -a -e error.log -a  -l loger.log -c python3 ../webapp/views.py


#nohup python3 views.py >  /dev/null

forever start -a -e error.log -a  -l loger.log -c python3 ../webapp/views.py

sudo chmod 776 Am
#start cloudwatch

cd ../.forever

sudo chmod 776 loger.log
sudo chmod 776 error.log

sudo mv loger.log /opt/

cd

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/AmazonCloudWatch-config.json -s