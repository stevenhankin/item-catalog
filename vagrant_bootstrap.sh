#
# Steve Hankin 4th Sept 2017
#
sudo apt-get install python-pip -y
sudo apt-get install libcurl4-openssl-dev -y
sudo apt-get install python-dev -y
sudo pip install -r /vagrant/requirements.txt
#cd /vagrant && gunicorn application:app -b 0.0.0.0:8000
