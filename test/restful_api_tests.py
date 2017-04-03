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

class BloodDonorTestCase(ResourcesAPITestCase):
    donor_1_request={
        "firstname": "Roope",
        "telephone": "+35854611111"
    }

    donor_2_request={
        "Roope": "firstname",
        "+35854611111": "telephone"
    }

    

    def setUp(self):
        
        super(BloodDonorTestCase, self).setUp()
        self.url = resources.api.url_for(resources.BloodDonor,
                                         donorId="bdonor-2",
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.BloodDonor,
                                               donorId="donor-789",
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """        
        _url = "/bloodalert/donors/bdonor-2/"
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodDonor)
    
    def test_wrong_url(self):
        """
        Checks that GET Blood Donor return correct status code if given a
        wrong message
        """
        print "("+self.test_wrong_url.__name__+")", self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)      
    def test_get_blood_donor_correct_status_code_headers(self):
        """
        Checks that GET Blood Donor return correct status code and content type in headers
        """
        print "("+self.test_get_blood_donor_correct_status_code_headers.__name__+")", self.test_get_blood_donor_correct_status_code_headers.__doc__        
        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_DONOR_PROFILE))
    def test_get_blood_donor(self):
        """
        Checking that GET Blood Donor return correct status code and hypermedia
        """

        print "("+self.test_get_blood_donor.__name__+")", self.test_get_blood_donor.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            print "\t Asserting that response has status code 200"
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            print "\tAsserting that @control has correct link relations"
            controls = data["@controls"]
            print "\t\tHas self and self has href={}".format(self.url)
            self.assertIn("self", controls)
            self.assertEqual(controls["self"]["href"],self.url)

            print "\t\tHas profile and profile has href={}".format(BLOODALERT_BLOOD_DONOR_PROFILE)
            self.assertIn("profile", controls)            
            self.assertEqual(controls["profile"]["href"],BLOODALERT_BLOOD_DONOR_PROFILE)

            print "\t\tHas collection and collection has href={}".format("/bloodalert/donors/")
            self.assertIn("collection", controls)            
            self.assertEqual(controls["collection"]["href"],"/bloodalert/donors/")
            
            print "\tAsserting that @controls has bloodalert:blood-donor-history-list and in correct format"
            self.assertIn("bloodalert:blood-donor-history-list", controls)
            all_donations=controls["bloodalert:blood-banks-all"]
            print "\t\t has title"
            self.assertIn("title", all_donations)
            print "\t\t has href and href={}history/".format(self.url)
            self.assertIn("href", all_donations)
            self.assertEquals(all_donations["href"], self.url+"history/")

            print "\tAsserting that @controls has bloodalert:delete and in correct format"
            self.assertIn("bloodalert:delete", controls)
            delete_ctrl=controls["bloodalert:delete"]
            print "\t\t has title"
            self.assertIn("title", delete_ctrl)
            print "\t\t has href and href={}".format(self.url)
            self.assertIn("href", delete_ctrl)
            self.assertEquals(delete_ctrl["href"], self.url)

            edit_donor_ctrl=controls["bloodalert:edit"]
            print "\t\t has title"
            self.assertIn("title", edit_donor_ctrl)
            print "\t\t has href and href={}".format(self.url)
            self.assertIn("href", edit_donor_ctrl)
            self.assertEquals(edit_donor_ctrl["href"], self.url)
            print "\t\t has encoding and encoding=json"
            self.assertIn("encoding", edit_donor_ctrl)
            self.assertEquals(edit_donor_ctrl["encoding"], "json")
            print "\t\t has method and method=PUT"
            self.assertIn("method", edit_donor_ctrl)
            self.assertEquals(edit_donor_ctrl["method"], "PUT")
            
            print "\t\t has schema and schema has all required atttributes type, propers, required"

            schema_data = add_donor_ctrl["schema"]
            
    def test_modify_blood_donor(self):
        """
        Modify an exsiting blood donor and check that the blood donor has been modified correctly 
        """
        print "("+self.test_modify_blood_donor.__name__+")", self.test_modify_blood_donor.__doc__

        resp = self.client.put(self.url,
                               data=json.dumps(self.donor_1_request),
                               headers={"Content-Type": JSON})
        print "\tAsserting that correctly modified blood donor returns status code 204"
        self.assertEquals(resp.status_code, 204)

        print "\tChecking that the blood donor was actually modified"        
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        print "\t\tAsserting that firstname was modified"
        self.assertEquals(data["firstname"], self.donor_1_request["firstname"])
        print "\t\tAsserting that telephone was modified"
        self.assertEquals(data["telephone"], self.donor_1_request["telephone"])   

    def test_modify_unexisting_blood_donor(self):
        """
        Trying to modify a non existent blood donor
        """
        print "("+self.test_modify_unexisting_blood_donor.__name__+")", self.test_modify_unexisting_blood_donor.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.donor_1_request),
                                headers={"Content-Type": JSON})
        print "\tAsserting that response returns status code 404"                       
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_body(self):
        """
        Try to modify a blood donor with wrong body
        """
        print "("+self.test_modify_wrong_body.__name__+")", self.test_modify_wrong_body.__doc__
        resp = self.client.put(self.url,
                               data=json.dumps(self.donor_2_request),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 400)
        

    def test_delete_blood_donor(self):
        """
        Checks that Delete Blood donor return correct status code if correctly delete
        """
        print "("+self.test_delete_blood_donor.__name__+")", self.test_delete_blood_donor.__doc__
        resp = self.client.delete(self.url)

        print "\tAsserting that response returns status code 204"
        self.assertEquals(resp.status_code, 204)
        print "\tChecking that the blood donor was actually deleted"
        print "\tAsserting that trying to load the deleted item returns 404"
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_wrong_url(self):
        """
        Checking that that Delete Blood donor returns correct status code if given a wrong address
        """
        print "("+self.test_delete_wrong_url.__name__+")", self.test_delete_wrong_url.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)    

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
    intial_donor_entries=8

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodDonors)
    def test_get_blood_donors_correct_status_code_headers(self):
        """
        Checks that GET Blood Donors return correct status code and content type in headers
        """
        print "("+self.test_get_blood_donors_correct_status_code_headers.__name__+")", self.test_get_blood_donors_correct_status_code_headers.__doc__

        
        resp = self.client.get(flask.url_for("blooddonors"))
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
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
        print "\tAsserting that response has status code 415"
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
        print "\tAsserting that response has status code 400"
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
    
    def test_get_blood_donors(self):
        """
        Checks that GET Messages return correct status code and data format
        """
        print "("+self.test_get_blood_donors.__name__+")", self.test_get_blood_donors.__doc__
       

        resp = self.client.get(flask.url_for("blooddonors"))
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)

        print "\tChecking correctness of hypermedia format"
        data = json.loads(resp.data)      
       
        controls = data["@controls"]
        print "\tAsserting that @controls has self link relation"
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        print "\tAsserting that @controls has bloodalert:blood-banks-all and in correct format"
        self.assertIn("bloodalert:blood-banks-all", controls)
        blood_banks_all=controls["bloodalert:blood-banks-all"]
        print "\t\t has title"
        self.assertIn("title", blood_banks_all)
        print "\t\t has href and href={}".format("/bloodalert/bloodbanks/")
        self.assertIn("href", blood_banks_all)
        self.assertEquals(blood_banks_all["href"], "/bloodalert/bloodbanks/")

        print "\tAsserting that @controls has bloodalert:add-blood-donor and in correct format"
        self.assertIn("bloodalert:add-blood-donor", controls)
        add_donor_ctrl=controls["bloodalert:add-blood-donor"]
        print "\t\t has title"
        self.assertIn("title", add_donor_ctrl)
        print "\t\t has href and href={}".format(self.url)
        self.assertIn("href", add_donor_ctrl)
        self.assertEquals(add_donor_ctrl["href"], self.url)
        print "\t\t has encoding and encoding=json"
        self.assertIn("encoding", add_donor_ctrl)
        self.assertEquals(add_donor_ctrl["encoding"], "json")
        print "\t\t has method and method=POST"
        self.assertIn("method", add_donor_ctrl)
        self.assertEquals(add_donor_ctrl["method"], "POST")
        print "\t\t has schema and schema has all required atttributes type, properties, required"

        schema_data = add_donor_ctrl["schema"]
        self.assertIn("type", schema_data)
        self.assertIn("properties", schema_data)
        self.assertIn("required", schema_data)
        print "\t\t\t Each schema property entry has required title,description,type"
        props = schema_data["properties"]
        for key, value in props.items():
            self.assertIn("description", value)
            self.assertIn("title", value)
            self.assertIn("type", value)
            self.assertEquals("string", value["type"])
        
        print "\tAsserting that response items and in correct format"
        items = data["items"]
        self.assertEquals(len(items), self.intial_donor_entries)
        for item in items:
            self.assertIn("donorId", item)
            self.assertIn("firstname", item)
            self.assertIn("birthDate", item)
            self.assertIn("gender", item)
            self.assertIn("telephone", item)
            self.assertIn("city", item)
            self.assertIn("address", item)
            self.assertIn("email", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertEquals(item["@controls"]["self"]["href"], resources.api.url_for(resources.BloodDonor, donorId=item["donorId"], _external=False))
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], BLOODALERT_BLOOD_DONOR_PROFILE)

        



if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()

    