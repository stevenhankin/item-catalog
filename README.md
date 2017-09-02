# Catalog App
This application is Steve Hankin's implementation of a project from the Udacity Full Stack Web Developer program.

# Features
* Amazon Login authentication
* CSRF protection

*Note: Also deploys to Heroku...sort of. Heroku starts multiple threads and uses an Emphemeral Filesystem; Sqlite is not reliable in such an environment and Postgres should be used instead (as a Heroku Addon). 
The database in this project is setup in-memory, but this does result in more that one instance in the application which can make changes appear to come and go.*

# Pre-requisites
* [Python3](https://www.python.org/downloads/)

# Installation
```
git clone https://github.com/stevenhankin/catalog
cd catalog
pip3 install -r requirements.txt
```

# Configuring to use Amazon Authentication
* Create an account on [Amazon Login](https://developer.amazon.com/lwa/sp/overview.html)
* Under the Security Profile / Web Settings:
  * Set Allowed Origins to be the application web address  (e.g. https://hankste-catalog.herokuapp.com)
  * Set Allowed Return URLs to be the /login route (e.g. https://hankste-catalog.herokuapp.com/login)
* Set YOUR_CLIENT_ID in config.py to match your Amazon Client ID (to authenticate using Amazon)

# Running application locally
## Directly using gunicorn (recommended)
```
gunicorn application:app
```
## Running on Heroku Platform
This project uses sqllite in-memory to make it more Heroku-friendly (albeit transient).
For same reason uses gunicorn so that processes are spawned rather than threads.
Follow these steps to deploy:
* Create an account and application on [Heroku](https://dashboard.heroku.com/apps)
  * New -> Create new app
  * Choose an app name and region, then Create app
  * Deployment method: Use Heroku CLI
  * Follow the remaining steps
* Run "heroku local" to test as a local instance 
* Finally, deploy to Heroku Platform using "git push heroku"

# FAQ
### I get the following error when trying to login:
```
We're sorry!
An error occurred when we tried to process your request. 
Rest assured, we're already working on the problem and expect to resolve it shortly.
```
*This is caused by incorrect account setup on Amazon Login. 
Please check you have the correct IDs and URL end-points configured.*
