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

<<<<<<< HEAD
forever start -a  -l loger.log -c python3 views.py
=======
>>>>>>> 0dcc76c62f702574fd4d0b6916a3619c729dd998
#start cloudwatch####

cd ../.forever

pwd
sudo chmod 776 loger.log



sudo mv loger.log /opt/

cd

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/AmazonCloudWatch-config.json -s