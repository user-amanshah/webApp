#!/bin/bash


#!/bin/bash



cd /home/ubuntu/webapp/




sudo forever stop -a  -l loger.log -c python3 views.py


sudo kill -9 `lsof -i:8080 -t`




###nohup python3 views.py >  /dev/null



sudo forever start -a  -l loger.log -c python3 views.py



#start cloudwatch####

cd ../.forever

sudo chmod 776 loger.log



sudo mv loger.log /opt/

cd

sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/AmazonCloudWatch-config.json -s


#comment