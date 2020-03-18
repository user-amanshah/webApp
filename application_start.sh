#!/bin/bash


#!/bin/bash



cd /home/ubuntu/webapp/


forever stop -a -e error.log -a  -l loger.log -c python3 views.py

sudo kill -9 `lsof -i:8080 -t`




#nohup python3 views.py >  /dev/null

forever start -a -e error.log -a  -l loger.log -c python3 views.py


#start cloudwatch

cd ../.forever

sudo chmod 776 loger.log


sudo mv loger.log /opt/

cd

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/AmazonCloudWatch-config.json -s