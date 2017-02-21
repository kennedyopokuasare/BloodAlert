
# Setting up the database
There are two options to setup ( create and populate) the databse. We recommend option 1 if you are not familiar with SQL

##  Option 1

* Ensure that you have python 2.7.x installed , and python path added to your environment variables
* open the command prompt at the root application (codes) folder
* run the command python -m setupdb

##  Option 2

* Database uses SQLite(www.sqlite.org) hence no installation is need, but ensure you have sqlite3.exe in the root of the project folder
* open command promt from the root folder of the project
* run the command sqlite3 db/bloodAlert.db   
* The previous step will take you to a prompt sqlite>
* run the command .read db/bloodAlert_schema_dump.sql
* rum the command .read db/bloodAlert_data_dump.sql

# Running Test Cases

* Ensure that you have python 2.7.x installed and python path added to your environment variables
* open the command prompt at the root application (codes) folder
* run the command python -m test.<name_of_test_file_without_.py_extension>
    * example python -m test.db_api_tests_blood_types


# Change logs

## Feb 20, 2017
* CRUD for Blood Banks, Blood Types
* Adapted Engine and Connection class from Exercise to work for our project
* Create the sql schema for the bloodAlert database
* Created the database

## Feb 21, 2017
*  Added Test Cases for Blood Type Database API
*  Added setupdb.py , a script to create and populate the database
* Added Instructions to setup database


