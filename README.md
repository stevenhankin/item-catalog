Place your catalog project in this directory.

# Pre-requisites
* [Git](https://git-scm.com/downloads)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)

# Running the application
* git clone https://github.com/stevenhankin/fullstack-nanodegree-vm.git
* cd fullstack-nanodegree-vm/vagrant && vagrant up && vagrant ssh
* gunicorn application:app --chdir /vagrant/catalog

# Running Application
Can be run on Heroku or in Vagrant

## Deploying to Heroku
This project uses sqllite in-memory to make it more Heroku-friendly (albeit transient).
For same reason uses gunicorn so that processes are spawned rather than threads.
Follow these steps to deploy:
* Create an account on [Amazon Login](https://developer.amazon.com/lwa/sp/overview.html)
* Use your 
* Create an account and application on [Heroku](https://dashboard.heroku.com/apps)


## Running in Vagrant
* cd vagrant
* vagrant up && vagrant ssh && gunicorn application:app --chdir /vagrant/catalog
