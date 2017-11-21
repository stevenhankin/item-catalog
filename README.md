# Catalog
Catalog is a web app that supports the categorisation of items for perusal (or modification if authenticated), and includes a rate-limited JSON API.

The application is a project from Udacity's [Full Stack Web Developer](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) course.

## Grader Information

#### IP Address and Port
* 35.177.46.95:2200 (Amazon Lightsail Server)

#### URL to hosted web application
* https://www.itemcatalog.club

#### Software and configuration changes
* Upgraded Linux packages and distribution
* UFW firewall (see **bootstrap.sh**) for SSH (port 2200), HTTP (port 80), and NTP (port 123) and SSL (port 443)
* Created a grader and catalog unix accounts 
* Created rsa public key for grader .ssh/authorized_keys
* Configured /etc/ssh/sshd_config to use authorized_keys
* Added grader to /etc/sudoers.d/90-cloud-init-users
* Installed and configured Apache (to use WSGI and SSL)
* Installed and configured Postgres
* Setup a catalog database user as application schema
* Converted Python code from SQLite to Postgres Database

#### 3rd party resources
* Amazon Lightsail Server
* Amazon Login authentication
* Apache SSL
* Domain name from [namecheap.com](https://www.namecheap.com)
* [Let's Encrypt Certbot](https://letsencrypt.org)

### Features
* CSRF protection
* API rate limiting
* Responsive design
* Heroku [demo site](https://hankste-catalog.herokuapp.com/)

## Pre-requisites
The required software can be installed by running the **bootstrap.sh**, which will additionally create a configure
the Postgres database.

## File list
* Procfile - __Heroku application startup method__
* README.md
* Vagrantfile - __Vagrant build file__
* application.py - __Main application entry__
* config.py - __Configuration parameters__
* database_populate.py - __Generate initial test data (called from *database_setup.py*)__
* database_setup.py - __Creates base schema. Called at application startup-up or directly when first installing__
* requirements.txt - __Python requirements in Vagrant VM__
* runtime.txt - __Heroku runtime engine requirement__
* static/ - __Images, stylesheets__
* templates/ - __Flask view templates__
* test/ - __Contains example CSRF test__
* bootstrap.sh - __Installs Python Libraries and other software when executed__


## Installation
Deploys to 3 different target environments, detailed below in order of suggested preference.

Local VM is most recommended since it will isolate the installation and configurations.  

Heroku is least recommended due to sqlite data layer; Sqlite is not reliable in such an environment and Postgres should be used instead (as a Heroku Addon). 
The database in this project is setup in-memory, but this does result in more that one instance in the application which can make changes appear to come and go.

### 1. Remote Linux Server Deployment
1. Clone the repository locally
2. Run ```bootstrap.sh```
3. Run ```python database_setup.py```
4. Add following section to **/etc/apache2/sites-enabled/000-default.conf** 
```Listen 443
<VirtualHost *:443>
    ServerName www.itemcatalog.club
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/www.itemcatalog.club/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/www.itemcatalog.club/privkey.pem
    WSGIScriptAlias / /var/www/html/myapp.wsgi
Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
```
5. Restart Apache ```sudo apache2ctl restart```
**Note:** Change the URLs above as required

#### 2. Local VM
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

#### 3. Local Host
1. Run the following:
```Shell
git clone https://github.com/stevenhankin/catalog
cd catalog
pip install -r requirements.txt
 gunicorn application:app
```
2. Open app in [browser](http://127.0.0.1:8000)

#### 4. Remotely on Heroku Platform
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


## Enabling 3rd Party OAuth (Amazon Authentication)
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
curl -H "Accept: application/json" https://www.itemcatalog.club/api/categories/1/items
```

2. Details for a specified item id
```Shell
/api/items/<int:item_id>
```
Example using curl command:
```Shell
curl -H "Accept: application/json" https://www.itemcatalog.club/api/items/1
```

### Testing the Rate Limiting for Developer API
A simple loop can quickly expose the "HTTP-429 Too Many Requests" reply:
```Shell
while [[ 1==1 ]]
do
curl -H "Accept: application/json" https://www.itemcatalog.club/api/categories/1/items
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
