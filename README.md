# BloodAlert
This is a fullstack implementation of BloodAlert - a social Campaign application for blood donation and blood banking 

# The Database
The Blood Alert Database API uses [SQLite](www.sqlite.org) hence no installation is needed

## Setting up the database
There are two options to setup (create and populate) the database. We recommend **option 1** if you are not familiar with SQL

###  Option 1
* Ensure that you have **python 2.7.x** installed , and python path added to your environment variables
* open the command prompt at the root of the application (codes) folder
* run the command 
    ````bash 
        python -m setupdb

###  Option 2
* Esure you have sqlite3.exe in the root of the project folder
* open command promt from the root folder of the application folder
* run the command sqlite3 db/bloodAlert.db   
* The previous step will take you to a prompt sqlite>
* run the following commands in the command prompt 
    ```bash 
        .read db/bloodAlert_schema_dump.sql
        .read db/bloodAlert_data_dump.sql

## Running Test Cases
* Ensure that you have **python 2.7.x** installed and python path added to your environment variables
* open the command prompt at the root application (codes) folder
* run the command using the command partern 
    ```bash 
        python -m test.<name_of_test_file_without_.py_extension>
* Examples of the commands to run the test cases are; 
    * example 1 **python -m test.db_api_tests_blood_types**
    * example 2 **python -m test.db_api_tests_blood_banks**
    * example 3 **python -m test.db_api_tests_blood_donors**






# The RESTFul API

The API is a follows the REST achitecture. 
The [full documentation](http://docs.bloodalert.apiary.io/#) of the API can be referenced here(http://docs.bloodalert.apiary.io/#)

The API was implemented using **FLASK microframework**(http://flask.pocoo.org/) which is a python framework.  
Other dependencies the API uses is the **Flask-RESTful** library

## Setting up and running 
To setup and run the API, please follow the following steps

1. Ensure that you have python 2.7.x installed , and python path added to your environment variables
2. Install FlASK microframework with the command
    ```bash
         pip install Flask
3. Install Flask-RESTful with the command 
    ```bash
        pip install flask-restful
4. Follow the steps in setting up the database descbribed above in **The Database** section, to setup the database
5. open the command prompt at the root of the application (codes) folder
6. run the command 
    ```bash
        python -m src.resources
7. The command in step 6  will start the FLASK built in web server with the address **http://localhost:5000** , or a similar address. The actual address will be displayed in the command prompt. 
8. The base URL to use to run the API will be **http://localhost:5000/bloodalert/** . Check the API documentation at **http://docs.bloodalert.apiary.io/#** for the various resources expossed by the API
9. You can now send request to the api using a web browser or a restclient like **postman**(https://www.getpostman.com), **Restlet Client** (https://restlet.com/documentation/client/user-guide) or even a web browser

## Running Test Cases
To run test cases of the RESTFul API
* Follow the steps 1-9 in the setting up and running the API instructions detailed above
* run the command 
    ```bash
        python -m test.restful_api_tests
* The command you just run will run all test cases in **test/restful_api_tests.py**
* To run specific tests run the command **python -m unittest test.restful_api_tests.name_of_specific_test_case_class**
    * Example 1 **python -m unittest test.restful_api_tests.BloodDonorsTestCase**
    * Example 2 **python -m unittest test.restful_api_tests.BloodBanksTestCase**
    * Example 3 **python -m unittest test.restful_api_tests.BloodBankHistoryTestCase**




# The Blood Alert Web Client 

The web client has a dependency on

* bootstrap(http://getbootstrap.com/)
* jquery (https://jquery.com/)
* Google Maps API (https://developers.google.com/maps/web/) , which is loaded over the internet

The goal of the client application is to bridge the gap between blood banks and their donors and also promote blood donation to blood banks.  The application provides a faster approach to finding a blood bank to donate blood.

The client application is a web application, which provides blood donors the functionality of registering as a donor and providing all their information. A registered donor can see his/her profile and modify the profile if needed. In addition, donor can see a list of all blood banks and check the blood levels status of each one of the blood banks, as well as the other information (e.g. address, telephone, etc) of a blood bank, based on which the donor can visit the blood bank and donate blood. Also, donor can check all his/her donation history.

The client also uses the **Google Maps API** to visualise the location of blood banks and their blood levels.

The client application use the **BloodAlert API**, in the implementation of its features. Detailed list of the API features of the client app,  and the specific resources in the API the client uses is as follows;

1. BloodBankList - Gets a list of all blood banks
2. BloodBank - Get the bloodBankId, name, address, city, telephone, latitude, longitude and threshold of a specific blood bank
3. BloodBank_Blood_Levels - Get the amount of bloods for all blood types of the target blood bank
4. DonorList - Add a new Blood donor into the database
5. Donor
    *   Get the donorId, firstname, familyName, birthDate, gender, bloodTypeId, telephone,city,address, email, of a blood donor
    *   Modifies any of (or a combination of ) the following ;firstname, familyName, birthDate, gender, bloodTypeId, telephone,             city,address email, of a blood donor
6. Donor_history_List - Get a list of Blood donor donation history in the database
7. BloodTypeList - Gets a list of Blood types



## Setting up and running 

Running the webclient will also run the RESTFul API
To setup and run the web client, please follow the following steps

1. Ensure that you have python 2.7.x installed , and python path added to your environment variables
2. Install FlASK microframework with the command
    ```bash
         pip install Flask
3. Install Flask-RESTful with the command 
    ```bash
        pip install flask-restful
4. Follow the steps in setting up the database descbribed above in **The Database** section, to setup the database
5. open the command prompt at the root of the application (codes) folder, and browse to **src** folder
6. run the command 
    ```bash
        python bloodalert.py
7. The command in step 6  will start a web server. You can now open the web client in a browsers
    with the address **http://localhost:5000/web** 
