#!/bin/bash


cd /opt/codedeploy-agent/deployment-root/deployment-instructions/
sudo rm -rf *-cleanup

cd
sudo kill -9 `lsof -i:8080 -t`