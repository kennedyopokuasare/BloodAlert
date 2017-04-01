
# The Database
The Blood Alert Database API uses
 [SQLite](www.sqlite.org) hence no installation is needed

## Setting up the database
There are two options to setup ( create and populate) the databse. We recommend option 1 if you are not familiar with SQL

###  Option 1

* Ensure that you have python 2.7.x installed , and python path added to your environment variables
* open the command prompt at the root application (codes) folder
* run the command **python -m setupdb**

###  Option 2

* Esure you have sqlite3.exe in the root of the project folder
* open command promt from the root folder of the project
* run the command sqlite3 db/bloodAlert.db   
* The previous step will take you to a prompt sqlite>
* run the command **.read db/bloodAlert_schema_dump.sql**
* rum the command **.read db/bloodAlert_data_dump.sql**

## Running Test Cases

* Ensure that you have python 2.7.x installed and python path added to your environment variables
* open the command prompt at the root application (codes) folder
* run the command **python -m test.<name_of_test_file_without_.py_extension>**
    * example 1 **python -m test.db_api_tests_blood_types**
    * example 2 **python -m test.db_api_tests_blood_banks**
    * example 3 **python -m test.db_api_tests_blood_donors**



* * *

# RESTFul API

The API is a follows the REST achitecture. 
The [full documentation](http://docs.bloodalert.apiary.io/#) of the API can be referenced here(http://docs.bloodalert.apiary.io/#)

The API was implemented using **FLASK microframework**(http://flask.pocoo.org/) which is a python framework.  
Other dependencies the API uses is the **Flask-RESTful** library

## Setting up and running 
To setup and run the API, please follow the following steps

1. Ensure that you have python 2.7.x installed , and python path added to your environment variables
2. Install FlASK microframework with the command **pip install Flask**
3. Install Flask-RESTful with the command **pip install flask-restful**
4. Follows steps in setting up the database descbribed above to setup the database
5. open the command prompt at the root application (codes) folder
6. run the command **python -m src.resources**
    * This will start the FLASK built in web server on the address **http://localhost:5000**
        * This address to use will also be displayed on the command prompt
    * The base URL to use will be **http://localhost:5000/bloodalert/** . Check the API documentation at **http://docs.bloodalert.apiary.io/#**
        for the various resources expossed by the API
    * You can now send request to the api using a web browser or a restclient like **postman**(https://www.getpostman.com), 
         **Restlet Client** (https://restlet.com/documentation/client/user-guide) or even a web browser

## Running Test Cases
To run test cases of the RESTFul API
* Follow the steps 1-5 in the setting up and running the API instructions detailed above
* run the command **python -m test.restful_api_tests**
    * This will run all test cases in test/restful_api_tests.py
    * To run specific tests run the command **python -m unittest test.restful_api_tests.name_of_specific_test_case_class**
        * Example **python -m unittest test.restful_api_tests.BloodDonorsTestCase**




