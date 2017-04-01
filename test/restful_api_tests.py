"""
Created on 30.03.2016
@author: asare
@author: anastasiia
@author: arash
"""

import unittest, copy
import json

import flask

import src.resources as resources
import src.database as database


BLOODALERT_BLOOD_BANK_PROFILE = "/profiles/blood-bank-profile/"
BLOODALERT_BLOOD_DONOR_PROFILE = "/profiles/blood-donor-profile/"
BLOODALERT_BLOOD_TYPES_PROFILE = "/profiles/blood-types-profile/"

ERROR_PROFILE = "/profiles/error-profile"
DB_PATH = "db/bloodalert_test.db"

ENGINE = database.Engine(DB_PATH)
MASON_JSON = "application/vnd.mason+json"
JSON = "application/json"

APIARY_PROFILES_URL = "http://docs.bloodalert.apiary.io/#reference/profiles/"
APIARY_RELS_URL = "http://docs.bloodalert.apiary.io/#reference/link-relations/"

NAMESPACE="bloodalert"
LINK_RELATIONS_URL = "/bloodalart/link-relations/"


# The following code was imported from PWP Exerice 4 

#Tell Flask that I am running it in testing mode.
resources.app.config["TESTING"] = True
#Necessary for correct translation in url_for
resources.app.config["SERVER_NAME"] = "localhost:5000"

#Database Engine utilized in our testing

resources.app.config.update({"Engine": ENGINE})


class ResourcesAPITestCase(unittest.TestCase):
    #INITIATION AND TEARDOWN METHODS
    @classmethod
    def setUpClass(cls):
        """ Creates the database structure. Removes first any preexisting
            database file
        """
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        """Remove the testing database"""
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        """
        Populates the database
        """
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()
        #Activate app_context for using url_for
        self.app_context = resources.app.app_context()
        self.app_context.push()
        #Create a test client
        self.client = resources.app.test_client()

    def tearDown(self):
        """
        Remove all records from database
        """
        ENGINE.clear()
        self.app_context.pop()

# End of Imported code

class BloodDonorsTestCase(ResourcesAPITestCase):
    donor_1_request={
            "firstname": "Anna",
            "familyName": "Bord",
            "telephone": "+348416754234",
            "email": "AnB@oulu.fi",
            "bloodTypeId": "btype-1",
            "birthDate": "30-12-1986",
            "gender": "Female",
            "address": "Yliopistokatu 46 , Linnanmaa",
            "city": "Oulu"
    }

    # Missing required firstname
    donor_2_request={            
            "familyName": "Bord",
            "telephone": "+348416754234",
            "email": "AnB@oulu.fi",
            "bloodTypeId": "btype-1",
            "birthDate": "30-12-1986",
            "gender": "Female",
            "address": "Yliopistokatu 46 , Linnanmaa",
            "city": "Oulu"
    }

    donor_3_request={
            "firstname": "Nana",
            "familyName": "Yaw",
            "telephone": "+348416754234",
            "email": "nanayaw@oulu.fi",
            "bloodTypeId": "btype-1",
            "birthDate": "30-12-1986",
            "gender": "Female",
            "address": "Yliopistokatu 46 , Linnanmaa",
            "city": "Oulu"
    }

    url="/bloodalert/donors/"

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodDonors)
    def test_get_blood_donors_correct_code_and_format(self):
        """
        Checks that GET Blood Donors return correct status code and data format
        """
        print "("+self.test_get_blood_donors_correct_code_and_format.__name__+")", self.test_get_blood_donors_correct_code_and_format.__doc__

        #Check that I receive status code 200
        resp = self.client.get(flask.url_for("blooddonors"))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_DONOR_PROFILE))
    def test_add_blood_donor_wrong_media(self):
        """
        Test  Add Blood Donor with a media different than json
        """
        print "("+self.test_add_blood_donor_wrong_media.__name__+")", self.test_add_blood_donor_wrong_media.__doc__
        resp = self.client.post(resources.api.url_for(resources.BloodDonors),
                                headers={"Content-Type": "text"},
                                data=self.donor_1_request.__str__()
                               )
        self.assertTrue(resp.status_code == 415)                     
    def test_add_blood_donor_incorrect_body_format(self):
        """
        Test that add blood donors response correctly when sending erroneous donor 
        format.
        """
        print "("+self.test_add_blood_donor_incorrect_body_format.__name__+")", self.test_add_blood_donor_incorrect_body_format.__doc__
        resp = self.client.post(resources.api.url_for(resources.BloodDonors),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.donor_2_request)
                               )
        self.assertTrue(resp.status_code == 400)
    def test_add_blood_donor(self):
        """
        Test that blood donor is added to the database.
        """
        print "("+self.test_add_blood_donor.__name__+")", self.test_add_blood_donor.__doc__

        resp = self.client.post(resources.api.url_for(resources.BloodDonors),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.donor_3_request)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get("Location")
        print "\tAsserting that Location header has url for created blood donor "
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        print "\tAsserting that new URL {} is correct and load data".format(url)
        self.assertTrue(resp.status_code == 200)




if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()

    