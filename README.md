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

* initialize db
    1. Create a db named PIN
    2. Create a table named entries with two text fields named (title, text)
    3. (Optional) Insert several random testing rows
    
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
