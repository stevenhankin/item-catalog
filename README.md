# Catalog
Catalog is a web app that supports the categorisation of items for perusal.  It demonstrates front-end/mid-tier/database coupling.

The application is a project from Udacity's [Full Stack Web Developer](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) course.


### Features
* Amazon Login authentication
* CSRF protection
* API rate limiting


## Pre-requisites
* [Python v2.7](https://www.python.org/downloads/)


## Installation
Can deploy to 3 different target environments, in order of suggested preference.

Local VM is most recommended since it will isolate the installation and configurations.  

Heroku is least recommended due to sqlite data layer; Sqlite is not reliable in such an environment and Postgres should be used instead (as a Heroku Addon). 
The database in this project is setup in-memory, but this does result in more that one instance in the application which can make changes appear to come and go.
####1. Local VM
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html)
2. Run the following:
```Shell
git clone https://github.com/stevenhankin/catalog
cd catalog
vagrant up
vagrant ssh
cd /vagrant
gunicorn application:app -b 0.0.0.0:8000
```
3. Open app in [browser](http://0.0.0.0:8000)

####2. Local Host
1. Run the following:
```Shell
git clone https://github.com/stevenhankin/catalog
cd catalog
pip install -r requirements.txt
 gunicorn application:app
```
2. Open app in [browser](http://127.0.0.1:8000)

####3. Remotely on Heroku Platform
1. Create an account on [Heroku](https://dashboard.heroku.com/apps) website
2. Create a new app
3. Run the following:
```
git clone https://github.com/stevenhankin/catalog
cd catalog
heroku git:remote -a <your_new_app_name>
git push heroku master
```
4. Access the application from the Heroku console using the "Open app" button


## Enabling Amazon Authentication
If you want users to login (which is required for modifications), then you'll need an Amazon Login account.
* Create an account on [Amazon Login](https://developer.amazon.com/lwa/sp/overview.html)
* Under the Security Profile / Web Settings:
  * Set Allowed Origins to be your machine's application web address  (e.g. https://hankste-catalog.herokuapp.com)
  * Set Allowed Return URLs to be the /login route (e.g. https://hankste-catalog.herokuapp.com/login)
* Set YOUR_CLIENT_ID in config.py to match your Amazon Client ID (also under the Web Settings)


## Developer API
To access the JSON data structure for an entity, make a request with the mime type set to 'application/json'

1. List of items within a specified category id
```Shell
/api/categories/<int:category_id>/items
```
Example using curl command:
```Shell
curl -H "Accept: application/json" http://127.0.0.1:8000/categories/1/items
```

2. Details for a specified item id
```Shell
/api/categories/items/<int:item_id>
```
Example using curl command:
```Shell
curl -H "Accept: application/json" http://127.0.0.1:8000/categories/items/1
```

### Testing the Rate Limiting for Developer API
A simple loop can quickly expose the "HTTP-429 Too Many Requests" reply:
```Shell
while [[ 1==1 ]]
do
curl -H "Accept: application/json" http://127.0.0.1:8000/api/categories/items/1
sleep 0.2
done
```



## FAQ
### I get the following error when trying to login to app:
```
We're sorry!
An error occurred when we tried to process your request. 
Rest assured, we're already working on the problem and expect to resolve it shortly.
```
*This is caused by incorrect account setup on Amazon Login. 
Please check you have the correct IDs and URL end-points configured.*
