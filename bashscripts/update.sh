#! /bin/bash
cd /bots/tommy
git fetch --all
git reset --hard origin/master
git pull origin master
sudo chown root:root /bots/tommy/bashscripts/*
sudo chmod 777 /bots/tommy/bashscripts/*
