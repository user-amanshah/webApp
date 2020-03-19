#!/bin/bash

mkdir -p /home/ubuntu/webapp
cd /home/ubuntu/webapp

sudo chmod 777 attachments


sudo pip3 install -r requirements.txt

cd /home/ubuntu/webapp
sudo chmod 776 AmazonCloudWatch-config.json
sudo mv AmazonCloudWatch-config.json /opt