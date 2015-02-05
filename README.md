Indigo
======

[![Build Status](https://travis-ci.org/Code4SA/indigo.svg)](http://travis-ci.org/Code4SA/indigo)

Indigo is AfricanLII's document management system for managing, capturing and publishing
legislation in the [Akoma Ntoso](http://www.akomantoso.org/) format.

It is a Django python web application with three components:

* a web-based editor
* a REST API for managing and authoring documents
* a REST API for vending legislative documents in HTML and XML

Local development
-----------------

Clone the repo and ensure you have python, virtualenv and pip installed. 

```bash
virtualenv env --no-site-packages
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Production deployment
---------------------

Production deployment assumes you're running on heroku.

You will need

* a django secret key
* a New Relic license key

```bash
heroku create
heroku addons:add heroku-postgresql
heroku addons:add newrelic:stark
heroku config:set DJANGO_DEBUG=false \
                  DJANGO_SECRET_KEY=some-secret-key \
                  NEW_RELIC_APP_NAME="Indigo" \
                  NEW_RELIC_LICENSE_KEY=some-license-key
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

License
-------

The project is licensed under a [GNU GPL 3 license](LICENSE).
