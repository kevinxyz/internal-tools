internal-tools
==============

Internal tools for a company/startup built on top of LDAP. Includes http://who, http://go, ...On your development machine, make sure to add the followings to your
/etc/hosts (adjust the IP to your actual VM IP):
172.16.238.88  qa-labs
172.16.238.88  qa-go
172.16.238.88  qa-dsso
172.16.238.88  qa-who

sudo apt-get install make python-pip python-dev libpq-dev libxml2-dev nginx
sudo apt-get install postgresql python-psycopg2 python-django-south python-ldap
sudo pip install Django==1.4.1 South==0.7.3 psycopg2==2.4.5 PyYAML==3.10
sudo pip install uWSGI==1.0.4
sudo apt-get install python-tornado

To launch in standalone mode for debugging purpose:
% cd dssodjango
% make run.test_server

To launch in nginx mode:
% make run.dev_servers
% make stop.dev_servers
