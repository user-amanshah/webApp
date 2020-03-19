#!/bin/bash


cd /opt/codedeploy-agent/deployment-root/deployment-instructions/
sudo rm -rf *-cleanup

cd
sudo apt-get update
sudo curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm i -g forever --save


cd
pwd



