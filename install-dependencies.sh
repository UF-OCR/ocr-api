#! /bin/sh
# this is a work in progress and written only for linux installations
yum install epel-release 
yum install python-pip
sudo yum install python-virtualenv
virtualenv sqlalchemy-workspace
cd sqlalchemy-workspace
source bin/activate
pip install sqlalchemy
pip install PyLD
pip install cx_Oracle --upgrade
