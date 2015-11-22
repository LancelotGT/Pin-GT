## Pin@GT
A web app that let GT students quickly explore the current events on campus.

## Dependencies
* Flask
* MySQLdb
* flask-mysql
* virtualenv (recommended)

## Project structure
PinGT/

    templates/

    static/

    schema.sql
    
    PinGT.py

## Steps to run
* install db, management tools
    * mysql
    * virtualenv
    * git

* <s>initialize db</s>
    1. <s>Create a db named PIN</s>
    2. <s>Create a table named entries with two text fields named (title, text)</s>
    3. <s>(Optional) Insert several random testing rows</s>

* no need to init db now. It is running on a EC2 instance.

* install dependencies
```
git clone https://github.com/LancelotGT/PinGT.git
cd PinGT
virtualenv venv
. venv/bin/activate
pip install Flask
pip install requests
pip install mysql
pip install flask-mysql
```

* start app
```
python PinGT.py
```
Then go to `localhost:5000`.

## TODO
Create a script to initialize mysql db
