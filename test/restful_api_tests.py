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
BLOODALERT_BLOOD_TYPE_PROFILE = "/profiles/blood-types-profile/"

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
        print "\nTesting ", cls.__name__
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


class BloodBankHistoryListTestCase(ResourcesAPITestCase):

    url="/bloodalert/bloodbanks/bbank-2/history/"
    def test_url(self):
        """
        Checks that the URL points to the right resource

        """
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodBankHistoryList)
    def test_get_blood_bank_history_list_correct_status_code_headers(self):
        """
        Checks that GET Blood Bank History List return correct status code and content type in headers
        """
        print "("+self.test_get_blood_bank_history_list_correct_status_code_headers.__name__+")", self.test_get_blood_bank_history_list_correct_status_code_headers.__doc__

        
        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_BANK_PROFILE))
    def test_get_blood_bank_history_list(self):
        """
        Checks that GET Blood bank history list return correct status code and data format
        """
        print "("+self.test_get_blood_bank_history_list.__name__+")", self.test_get_blood_bank_history_list.__doc__
       

        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)

        print "\tChecking correctness of hypermedia format"
        data = json.loads(resp.data)      
       
        controls = data["@controls"]
        print "\tAsserting that @controls has self link relation"
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        print "\tAsserting that @controls has bloodalert:blood-bank-blood-level and in correct format"
        self.assertIn("bloodalert:blood-bank-blood-level", controls)
        all_blood_level=controls["bloodalert:blood-bank-blood-level"]
        print "\t\t has title"
        self.assertIn("title", all_blood_level)
        blood_levels_url=resources.api.url_for(resources.BloodBankBloodLevels,bloodBankId="bbank-2",_external=False)
        print "\t\t has href and href={}".format(blood_levels_url)
        self.assertIn("href", all_blood_level)
        self.assertEquals(all_blood_level["href"], blood_levels_url)      

   
        print "\tAsserting that response items and in correct format"
        items = data["items"]
        
        for item in items:
            self.assertIn("historyId", item)
            self.assertIn("donorId", item)
            self.assertIn("bloodTypeId", item)
            self.assertIn("bloodBankId", item)
            self.assertIn("amount", item)           
            self.assertIn("timeStamp", item)
            self.assertIn("tag", item)
            
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertEquals(item["@controls"]["self"]["href"],resources.api.url_for(resources.BloodBankHistory, bloodBankId=item["bloodBankId"],historyId=item["historyId"],_external=False))

            self.assertIn("bloodbank", item["@controls"])
            self.assertEquals(item["@controls"]["bloodbank"]["href"], resources.api.url_for(resources.BloodBank, bloodBankId=item["bloodBankId"],_external=False))

            self.assertIn("bloodtype", item["@controls"])
            self.assertEquals(item["@controls"]["bloodtype"]["href"], resources.api.url_for(resources.BloodType, bloodTypeId=item["bloodTypeId"],_external=False))

            self.assertIn("donor", item["@controls"])
            self.assertEquals(item["@controls"]["donor"]["href"], resources.api.url_for(resources.BloodDonor, donorId=item["donorId"],_external=False))
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], BLOODALERT_BLOOD_BANK_PROFILE)
class BloodBankHistoryTestCase(ResourcesAPITestCase):
    history_1={
        "timeStamp": "2016-09-18 11:31:12",
        "amount": 250,
        "tag": "DONATION",
        "donorId": "bdonor-1",
        "bloodTypeId": "btype-1"
    }
    history_2={        
        "amount": 100,        
        "donorId": "bdonor-2"
    }

    history_3={        
        "100": "amount",        
        "bdonor-2": "donor"
    }
    def setUp(self):
        
        super(BloodBankHistoryTestCase, self).setUp()
        self.url = resources.api.url_for(resources.BloodBankHistory,
                                         bloodBankId="bbank-1",historyId='history-1',
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.BloodBankHistory,
                                                bloodBankId="bbank-1",historyId='history-2000',
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """        
        _url = "/bloodalert/bloodbanks/bbank-1/history/history-1/"
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodBankHistory)
    
    def test_wrong_url(self):
        """
        Checks that GET Blood bank history return correct status code if given a
        wrong URL
        """
        print "("+self.test_wrong_url.__name__+")", self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)
    
    def test_modify_blood_bank_history(self):
        """
        Modify an exsiting blood bank history and check that the blood bank history has been modified correctly 
        """
        print "("+self.test_modify_blood_bank_history.__name__+")", self.test_modify_blood_bank_history.__doc__

        resp = self.client.put(self.url,
                               data=json.dumps(self.history_2),
                               headers={"Content-Type": JSON})
        print "\tAsserting that correctly modified blood bank history returns status code 204"
        self.assertEquals(resp.status_code, 204)

        print "\tChecking that the blood bank history was actually modified"        
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        print "\t\tAsserting that amount was modified"
        self.assertEquals(data["amount"], self.history_2["amount"])
        print "\t\tAsserting that donorId was modified"
        self.assertEquals(data["donorId"], self.history_2["donorId"])   

    def test_modify_unexisting_blood_bank_history(self):
        """
        Trying to modify a non existent blood bank history
        """
        print "("+self.test_modify_unexisting_blood_bank_history.__name__+")", self.test_modify_unexisting_blood_bank_history.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.history_2),
                                headers={"Content-Type": JSON})
        print "\tAsserting that response returns status code 404"                       
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_body(self):
        """
        Try to modify a blood bank history with wrong body
        """
        print "("+self.test_modify_wrong_body.__name__+")", self.test_modify_wrong_body.__doc__
        
        resp = self.client.put(self.url,
                               data=json.dumps(self.history_3),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 500)
        

    def test_delete_blood_bank_history(self):
        """
        Checks that Delete Blood bank history return correct status code if correctly delete
        """
        print "("+self.test_delete_blood_bank_history.__name__+")", self.test_delete_blood_bank_history.__doc__
        resp = self.client.delete(self.url)

        print "\tAsserting that response returns status code 204"
        self.assertEquals(resp.status_code, 204)
        print "\tChecking that the blood bank history was actually deleted"
        print "\tAsserting that trying to load the deleted item returns 404"
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_wrong_url(self):
        """
        Checking that that Delete Blood bank history returns correct status code if given a wrong address
        """
        print "("+self.test_delete_wrong_url.__name__+")", self.test_delete_wrong_url.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)

class BloodBanksTestCase(ResourcesAPITestCase):
    blood_bank_1={
        "name": "Oulun Tervestalo Veri Palvelu",
        "address": "Kajaanintie 50",
        "city": "Oulu",
        "telephone": "+358 8 3152011",
        "email": "OuluUniHospital@oulu.fi",
        "latitude": 65.007406,
        "longitude": 25.517786,
        "threshold": 30
    }

    blood_bank_2={        
        "address": "Kajaanintie 50",
        "city": "Oulu",       
        "latitude": 65.007406,
        "longitude": 25.517786,
        "threshold": 30
    }

    blood_bank_3={
        "name": "Tampere University Hospital",
        "address": "Yliopistonkatu 50",
        "city": "Tampere",
        "telephone": "+358 8 3152011",
        "email": "TampereUniHospital@oulu.fi",
        "latitude": 65.007406,
        "longitude": 25.517786,
        "threshold": 30
    }

    url="/bloodalert/bloodbanks/"
    intial__blood_banks_entries=4
    def test_url(self):
        """
        Checks that the URL points to the right resource
        
        """
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodBanks)
    def test_get_blood_banks_correct_status_code_headers(self):
        """
        Checks that GET Blood Banks return correct status code and content type in headers
        """
        print "("+self.test_get_blood_banks_correct_status_code_headers.__name__+")", self.test_get_blood_banks_correct_status_code_headers.__doc__

        
        resp = self.client.get(flask.url_for("bloodbanks"))
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_BANK_PROFILE))
    def test_add_blood_bank_wrong_media(self):
        """
        Test  Add Blood Bank with a media different than json
        """
        print "("+self.test_add_blood_bank_wrong_media.__name__+")", self.test_add_blood_bank_wrong_media.__doc__
        resp = self.client.post(resources.api.url_for(resources.BloodBanks),
                                headers={"Content-Type": "text"},
                                data=self.blood_bank_1.__str__()
                               )
        print "\tAsserting that response has status code 415"
        self.assertTrue(resp.status_code == 415)                     
    def test_add_blood_bank_incorrect_body_format(self):
        """
        Test that add blood bank response correctly when sending erroneous blood bank format.
        """
        print "("+self.test_add_blood_bank_incorrect_body_format.__name__+")", self.test_add_blood_bank_incorrect_body_format.__doc__
        resp = self.client.post(resources.api.url_for(resources.BloodBanks),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.blood_bank_2)
                               )
        print "\tAsserting that response has status code 400"
        self.assertTrue(resp.status_code == 400)
    def test_add_blood_bank(self):
        """
        Test that blood bank is added to the database.
        """
        print "("+self.test_add_blood_bank.__name__+")", self.test_add_blood_bank.__doc__

        resp = self.client.post(resources.api.url_for(resources.BloodBanks),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.blood_bank_3)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get("Location")
        print "\tAsserting that Location header has url for created blood donor "
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        print "\tAsserting that new URL {} is correct and load data".format(url)
        self.assertTrue(resp.status_code == 200)
    
    def test_get_blood_banks(self):
        """
        Checks that GET Blood banks return correct status code and data format
        """
        print "("+self.test_get_blood_banks.__name__+")", self.test_get_blood_banks.__doc__
       

        resp = self.client.get(flask.url_for("bloodbanks"))
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)

        print "\tChecking correctness of hypermedia format"
        data = json.loads(resp.data)      
       
        controls = data["@controls"]
        print "\tAsserting that @controls has self link relation"
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        print "\tAsserting that @controls has bloodalert:blood-types-all and in correct format"
        self.assertIn("bloodalert:blood-types-all", controls)
        blood_types_all=controls["bloodalert:blood-types-all"]
        print "\t\t has title"
        self.assertIn("title", blood_types_all)
        print "\t\t has href and href={}".format("/bloodalert/bloodtypes/")
        self.assertIn("href", blood_types_all)
        self.assertEquals(blood_types_all["href"], "/bloodalert/bloodtypes/")

        print "\tAsserting that @controls has bloodalert:donors-all and in correct format"
        self.assertIn("bloodalert:donors-all", controls)
        blood_banks_all=controls["bloodalert:donors-all"]
        print "\t\t has title"
        self.assertIn("title", blood_banks_all)
        print "\t\t has href and href={}".format("/bloodalert/donors/")
        self.assertIn("href", blood_banks_all)
        self.assertEquals(blood_banks_all["href"], "/bloodalert/donors/")

        print "\tAsserting that @controls has bloodalert:add-blood-bank and in correct format"
        self.assertIn("bloodalert:add-blood-bank", controls)
        add_blood_bank_ctrl=controls["bloodalert:add-blood-bank"]
        print "\t\t has title"
        self.assertIn("title", add_blood_bank_ctrl)
        print "\t\t has href and href={}".format(self.url)
        self.assertIn("href", add_blood_bank_ctrl)
        self.assertEquals(add_blood_bank_ctrl["href"], self.url)
        print "\t\t has encoding and encoding=json"
        self.assertIn("encoding", add_blood_bank_ctrl)
        self.assertEquals(add_blood_bank_ctrl["encoding"], "json")
        print "\t\t has method and method=POST"
        self.assertIn("method", add_blood_bank_ctrl)
        self.assertEquals(add_blood_bank_ctrl["method"], "POST")
        print "\t\t has schema and schema has all required atttributes type, properties, required"

        schema_data = add_blood_bank_ctrl["schema"]
        bloodBankSchema=resources.BloodAlertObject()._blood_bank_schema(edit=False)
        print "\t\t\tschema has type"
        self.assertIn("type", schema_data)
        print "\t\t\tschema has properties and in correct format with all attributes"
        self.assertIn("properties", schema_data)
        self.assertEquals(schema_data["properties"], bloodBankSchema["properties"])
        print "\t\t\tschema has required"
        self.assertIn("required", schema_data)
        self.assertEquals(schema_data["required"], bloodBankSchema["required"])
        
        print "\t\t\tEach schema property entry has required title,description,type"
        props = schema_data["properties"]

        numbertypes=["latitude","longitude","threshold"]

        for key, value in props.items():
            self.assertIn("description", value)
            self.assertIn("title", value)
            self.assertIn("type", value)
            if key in numbertypes:
                self.assertEquals("number", value["type"])
            else:
                self.assertEquals("string", value["type"])
        
        print "\tAsserting that response items and in correct format"
        items = data["items"]
        self.assertEquals(len(items), self.intial__blood_banks_entries)
        for item in items:
            self.assertIn("bloodBankId", item)
            self.assertIn("name", item)
            self.assertIn("address", item)
            self.assertIn("city", item)
            self.assertIn("telephone", item)
            self.assertIn("email", item)
            self.assertIn("latitude", item)
            self.assertIn("longitude", item)
            self.assertIn("threshold", item)
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertEquals(item["@controls"]["self"]["href"], resources.api.url_for(resources.BloodBank, bloodBankId=item["bloodBankId"], _external=False))
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], BLOODALERT_BLOOD_BANK_PROFILE)
    
    
class BloodBankTestCase(ResourcesAPITestCase):

    
    blood_bank_1={
        "city": "Tampere",               
        "threshold": 25,     
        "email": "tampere@oulu.fi"
    }
    blood_bank_2={
        "Tampere": "city",               
        "25": "threshold",     
        "tampere@oulu.fi": "email"
    }

    def setUp(self):        
        super(BloodBankTestCase, self).setUp()
        self.url = resources.api.url_for(resources.BloodBank,
                                         bloodBankId="bbank-1",
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.BloodBank,
                                               bloodBankId="bbank-789",
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """        
        _url = "/bloodalert/bloodbanks/bbank-1/"
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodBank)
    
    def test_wrong_url(self):
        """
        Checks that GET Blood blood bank return correct status code if given a
        wrong URL
        """
        print "("+self.test_wrong_url.__name__+")", self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404) 
    def test_get_blood_bank_correct_status_code_headers(self):
        """
        Checks that GET Blood bank return correct status code and content type in headers
        """
        print "("+self.test_get_blood_bank_correct_status_code_headers.__name__+")", self.test_get_blood_bank_correct_status_code_headers.__doc__        
        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_BANK_PROFILE))    
    def test_get_blood_bank(self):
        """
        Checking that GET Blood Bank return correct status code and MASON hypermedia format
        """

        print "("+self.test_get_blood_bank.__name__+")", self.test_get_blood_bank.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            print "\tAsserting that response has status code 200"
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            print "\tAsserting that @control has correct link relations"
            controls = data["@controls"]
            print "\t\tHas self and self has href={}".format(self.url)
            self.assertIn("self", controls)
            self.assertEqual(controls["self"]["href"],self.url)

            print "\t\tHas profile and profile has href={}".format(BLOODALERT_BLOOD_BANK_PROFILE)
            self.assertIn("profile", controls)            
            self.assertEqual(controls["profile"]["href"],BLOODALERT_BLOOD_BANK_PROFILE)

            print "\t\tHas collection and collection has href={}".format("/bloodalert/bloodbanks/")
            self.assertIn("collection", controls)            
            self.assertEqual(controls["collection"]["href"],"/bloodalert/bloodbanks/")
            
            print "\tAsserting that @controls has bloodalert:blood-bank-history-list and in correct format"
            self.assertIn("bloodalert:blood-bank-history-list", controls)
            all_history=controls["bloodalert:blood-bank-history-list"]
            print "\t\t has title"
            self.assertIn("title", all_history)
            print "\t\t has href and href={}history/".format(self.url)
            self.assertIn("href", all_history)
            self.assertEquals(all_history["href"], self.url+"history/")

            print "\tAsserting that @controls has bloodalert:blood-bank-blood-level and in correct format"
            self.assertIn("bloodalert:blood-bank-blood-level", controls)
            all_blood_level=controls["bloodalert:blood-bank-blood-level"]
            print "\t\t has title"
            self.assertIn("title", all_blood_level)
            print "\t\t has href and href={}bloodlevels/".format(self.url)
            self.assertIn("href", all_blood_level)
            self.assertEquals(all_blood_level["href"], self.url+"bloodlevels/")

            print "\tAsserting that @controls has bloodalert:delete and in correct format"
            self.assertIn("bloodalert:delete", controls)
            delete_ctrl=controls["bloodalert:delete"]
            print "\t\t has title"
            self.assertIn("title", delete_ctrl)
            print "\t\t has href and href={}".format(self.url)
            self.assertIn("href", delete_ctrl)
            self.assertEquals(delete_ctrl["href"], self.url)
            print "\t\t has method and method=DELETE"
            self.assertEquals(delete_ctrl["method"],"DELETE")

            print "\tAsserting that @controls has bloodalert:edit and in correct format"
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
            
            print "\t\thas schema and schema has all required atttributes type, properties, required"

            schema_data = edit_donor_ctrl["schema"]
            bloodBankSchema=resources.BloodAlertObject()._blood_bank_schema(edit=True)
            print "\t\t\tschema has type"
            self.assertIn("type", schema_data)
            print "\t\t\tschema has properties and in correct format with all attributes"
            self.assertIn("properties", schema_data)
            self.assertEquals(schema_data["properties"], bloodBankSchema["properties"])
            print "\t\t\tschema has required"
            self.assertIn("required", schema_data)
            self.assertEquals(schema_data["required"], bloodBankSchema["required"])

            print "\t\t\t Each schema property entry has required title,description,type"

            numbertypes=["latitude","longitude","threshold"]
            props = schema_data["properties"]
            for key, value in props.items():
                self.assertIn("description", value)
                self.assertIn("title", value)
                self.assertIn("type", value)
                if key in numbertypes:
                    self.assertEquals("number", value["type"])
                else:
                    self.assertEquals("string", value["type"])
    
    def test_modify_blood_bank(self):
        """
        Modify an exsiting blood bank and check that the blood bank has been modified correctly 
        """
        print "("+self.test_modify_blood_bank.__name__+")", self.test_modify_blood_bank.__doc__

        resp = self.client.put(self.url,
                               data=json.dumps(self.blood_bank_1),
                               headers={"Content-Type": JSON})
        print "\tAsserting that correctly modified blood bank returns status code 204"
        self.assertEquals(resp.status_code, 204)

        print "\tChecking that the blood bank was actually modified"        
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        print "\t\tAsserting that city was modified"
        self.assertEquals(data["city"], self.blood_bank_1["city"])
        print "\t\tAsserting that threshold was modified"
        self.assertEquals(data["threshold"], self.blood_bank_1["threshold"])  
        print "\t\tAsserting that email was modified"
        self.assertEquals(data["email"], self.blood_bank_1["email"])    

    def test_modify_unexisting_blood_bank(self):
        """
        Trying to modify a non existent blood bank
        """
        print "("+self.test_modify_unexisting_blood_bank.__name__+")", self.test_modify_unexisting_blood_bank.__doc__
        resp = self.client.put(self.url_wrong,
                                data=json.dumps(self.blood_bank_1),
                                headers={"Content-Type": JSON})
        print "\tAsserting that response returns status code 404"                       
        self.assertEquals(resp.status_code, 404)

    def test_modify_wrong_body(self):
        """
        Try to modify a blood donor with wrong body
        """
        print "("+self.test_modify_wrong_body.__name__+")", self.test_modify_wrong_body.__doc__
        
        resp = self.client.put(self.url,
                               data=json.dumps(self.blood_bank_2),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 500)  
    def test_delete_blood_bank(self):
        """
        Checks that Delete Blood bank return correct status code if correctly delete
        """
        print "("+self.test_delete_blood_bank.__name__+")", self.test_delete_blood_bank.__doc__
        resp = self.client.delete(self.url)

        print "\tAsserting that response returns status code 204"
        self.assertEquals(resp.status_code, 204)
        print "\tChecking that the blood donor was actually deleted"
        print "\tAsserting that trying to load the deleted item returns 404"
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    def test_delete_wrong_url(self):
        """
        Checking that that Delete Blood bank returns correct status code if given a wrong address
        """
        print "("+self.test_delete_wrong_url.__name__+")", self.test_delete_wrong_url.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)             
class BloodTypesTestCase(ResourcesAPITestCase):
    url="/bloodalert/bloodtypes/"
    intial_blood_types_entries=8
    blood_type_1={
        "name": "O++"
    }
    blood_type_2={
        "someName": "O+"
    }

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """
        print "("+self.test_url.__name__+")", self.test_url.__doc__,
        with resources.app.test_request_context(self.url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodTypes)
    def test_get_blood_types_correct_status_code_headers(self):
        """
        Checks that GET Blood types return correct status code and content type in headers
        """
        print "("+self.test_get_blood_types_correct_status_code_headers.__name__+")", self.test_get_blood_types_correct_status_code_headers.__doc__

        
        resp = self.client.get(flask.url_for("bloodtypes"))
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_TYPE_PROFILE))
    def test_add_blood_type_wrong_media(self):
        """
        Test  Add Blood type with a media different than json
        """
        print "("+self.test_add_blood_type_wrong_media.__name__+")", self.test_add_blood_type_wrong_media.__doc__
        resp = self.client.post(resources.api.url_for(resources.BloodTypes),
                                headers={"Content-Type": "text"},
                                data=self.blood_type_1.__str__()
                               )
        print "\tAsserting that response has status code 415"
        self.assertTrue(resp.status_code == 415)  
    def test_add_blood_type_incorrect_body_format(self):
        """
        Test that add blood type response correctly when sending erroneous blood types 
        format.
        """
        print "("+self.test_add_blood_type_incorrect_body_format.__name__+")", self.test_add_blood_type_incorrect_body_format.__doc__
        resp = self.client.post(resources.api.url_for(resources.BloodTypes),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.blood_type_2)
                               )
        print "\tAsserting that response has status code 400"
        self.assertTrue(resp.status_code == 400)
    def test_add_blood_type(self):
        """
        Test that blood type is added to the database.
        """
        print "("+self.test_add_blood_type.__name__+")", self.test_add_blood_type.__doc__

        resp = self.client.post(resources.api.url_for(resources.BloodTypes),
                                headers={"Content-Type": JSON},
                                data=json.dumps(self.blood_type_1)
                               )
        self.assertTrue(resp.status_code == 201)
        url = resp.headers.get("Location")
        print "\tAsserting that Location header has url for created blood type "
        self.assertIsNotNone(url)
        resp = self.client.get(url)
        print "\tAsserting that new URL {} is correct and load data".format(url)
        self.assertTrue(resp.status_code == 200)
    def test_get_blood_types(self):
        """
        Checks that GET Blood Types return correct status code and data format
        """
        print "("+self.test_get_blood_types.__name__+")", self.test_get_blood_types.__doc__
       

        resp = self.client.get(flask.url_for("bloodtypes"))
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)

        print "\tChecking correctness of hypermedia format"
        data = json.loads(resp.data)      
       
        controls = data["@controls"]
        print "\tAsserting that @controls has self link relation"
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        print "\tAsserting that @controls has bloodalert:donors-all and in correct format"
        self.assertIn("bloodalert:donors-all", controls)
        blood_banks_all=controls["bloodalert:donors-all"]
        print "\t\t has title"
        self.assertIn("title", blood_banks_all)
        print "\t\t has href and href={}".format("/bloodalert/donors/")
        self.assertIn("href", blood_banks_all)
        self.assertEquals(blood_banks_all["href"], "/bloodalert/donors/")

        print "\tAsserting that @controls has bloodalert:donors-all and in correct format"
        self.assertIn("bloodalert:donors-all", controls)
        blood_banks_all=controls["bloodalert:donors-all"]
        print "\t\t has title"
        self.assertIn("title", blood_banks_all)
        print "\t\t has href and href={}".format("/bloodalert/donors/")
        self.assertIn("href", blood_banks_all)
        self.assertEquals(blood_banks_all["href"], "/bloodalert/donors/")

        print "\tAsserting that @controls has bloodalert:add-blood-type and in correct format"
        self.assertIn("bloodalert:add-blood-type", controls)
        add_blood_type_ctrl=controls["bloodalert:add-blood-type"]
        print "\t\t has title"
        self.assertIn("title", add_blood_type_ctrl)
        print "\t\t has href and href={}".format(self.url)
        self.assertIn("href", add_blood_type_ctrl)
        self.assertEquals(add_blood_type_ctrl["href"], self.url)
        print "\t\t has encoding and encoding=json"
        self.assertIn("encoding", add_blood_type_ctrl)
        self.assertEquals(add_blood_type_ctrl["encoding"], "json")
        print "\t\t has method and method=POST"
        self.assertIn("method", add_blood_type_ctrl)
        self.assertEquals(add_blood_type_ctrl["method"], "POST")
        print "\t\t has schema and schema has all required atttributes type, properties, required"

        schema_data = add_blood_type_ctrl["schema"]
        bloodTypeSchema=resources.BloodAlertObject()._blood_type_schema()
        print "\t\t\tschema has type"
        self.assertIn("type", schema_data)
        print "\t\t\tschema has properties and in correct format with all attributes"
        self.assertIn("properties", schema_data)
        self.assertEquals(schema_data["properties"], bloodTypeSchema["properties"])
        print "\t\t\tschema has required"
        self.assertIn("required", schema_data)
        self.assertEquals(schema_data["required"], bloodTypeSchema["required"])
        
        print "\t\t\tEach schema property entry has required title,description,type"
        props = schema_data["properties"]
        for key, value in props.items():
            self.assertIn("description", value)
            self.assertIn("title", value)
            self.assertIn("type", value)
            self.assertEquals("string", value["type"])
        
        print "\tAsserting that response items and in correct format"
        items = data["items"]
        self.assertEquals(len(items), self.intial_blood_types_entries)
        for item in items:
            self.assertIn("bloodTypeId", item)
            self.assertIn("name", item)
            
            self.assertIn("@controls", item)
            self.assertIn("self", item["@controls"])
            self.assertIn("href", item["@controls"]["self"])
            self.assertEquals(item["@controls"]["self"]["href"], resources.api.url_for(resources.BloodType, bloodTypeId=item["bloodTypeId"], _external=False))
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], BLOODALERT_BLOOD_TYPE_PROFILE)

class BloodTypeTestCase(ResourcesAPITestCase):
    blood_type_1={
        "name": "O+"
        }
    blood_type_2={
        "someName": "O+"
        }
    blood_type_3={
        "name": "O++"
        }

    def setUp(self):
        super(BloodTypeTestCase, self).setUp()
        self.url = resources.api.url_for(resources.BloodType,
                                         bloodTypeId="btype-2",
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.BloodType,
                                               bloodTypeId="type-789",
                                               _external=False)
        self.url_unexisting_item = resources.api.url_for(resources.BloodType,
                                               bloodTypeId="btype-789",
                                               _external=False)
    def test_url(self):
        """
        Checks that the URL points to the right resource
        """        
        _url = "/bloodalert/bloodtypes/btype-2/"
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodType)
    def test_wrong_url(self):
        """
        Checks that GET Blood Type return correct status code if given a
        wrong URL
        """
        print "("+self.test_wrong_url.__name__+")", self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
    def test_get_blood_type_correct_status_code_headers(self):
        """
        Checks that GET Blood type return correct status code and content type in headers
        """
        print "("+self.test_get_blood_type_correct_status_code_headers.__name__+")", self.test_get_blood_type_correct_status_code_headers.__doc__        
        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_TYPE_PROFILE))
    
    def test_get_blood_type(self):
        """
        Checking that GET Blood Type return correct status code and MASON hypermedia format
        """

        print "("+self.test_get_blood_type.__name__+")", self.test_get_blood_type.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            print "\tAsserting that response has status code 200"
            self.assertEquals(resp.status_code, 200)
            data = json.loads(resp.data)

            print "\tAsserting that @control has correct link relations"
            controls = data["@controls"]
            print "\t\tHas self and self has href={}".format(self.url)
            self.assertIn("self", controls)
            self.assertEqual(controls["self"]["href"],self.url)

            print "\t\tHas profile and profile has href={}".format(BLOODALERT_BLOOD_TYPE_PROFILE)
            self.assertIn("profile", controls)            
            self.assertEqual(controls["profile"]["href"],BLOODALERT_BLOOD_TYPE_PROFILE)

            print "\t\tHas collection and collection has href={}".format("/bloodalert/bloodtypes/")
            self.assertIn("collection", controls)            
            self.assertEqual(controls["collection"]["href"],"/bloodalert/bloodtypes/")
            
            
            print "\tAsserting that @controls has bloodalert:delete and in correct format"
            self.assertIn("bloodalert:delete", controls)
            delete_ctrl=controls["bloodalert:delete"]
            print "\t\t has title"
            self.assertIn("title", delete_ctrl)
            print "\t\t has href and href={}".format(self.url)
            self.assertIn("href", delete_ctrl)
            self.assertEquals(delete_ctrl["href"], self.url)
            print "\t\t has method and method=DELETE"
            self.assertEquals(delete_ctrl["method"],"DELETE")

            print "\tAsserting that @controls has bloodalert:delete and in correct format"
            edit_blood_type_ctrl=controls["bloodalert:edit"]
            print "\t\t has title"
            self.assertIn("title", edit_blood_type_ctrl)
            print "\t\t has href and href={}".format(self.url)
            self.assertIn("href", edit_blood_type_ctrl)
            self.assertEquals(edit_blood_type_ctrl["href"], self.url)
            print "\t\t has encoding and encoding=json"
            self.assertIn("encoding", edit_blood_type_ctrl)
            self.assertEquals(edit_blood_type_ctrl["encoding"], "json")
            print "\t\t has method and method=PUT"
            self.assertIn("method", edit_blood_type_ctrl)
            self.assertEquals(edit_blood_type_ctrl["method"], "PUT")
            
            print "\t\thas schema and schema has all required atttributes type, properties, required"
            schema_data = edit_blood_type_ctrl["schema"]
            bloodTypeSchema=resources.BloodAlertObject()._blood_type_schema()
            print "\t\t\tschema has type"
            self.assertIn("type", schema_data)
            print "\t\t\tschema has properties and in correct format with all attributes"
            self.assertIn("properties", schema_data)
            self.assertEquals(schema_data["properties"], bloodTypeSchema["properties"])
            print "\t\t\tschema has required"
            self.assertIn("required", schema_data)
            self.assertEquals(schema_data["required"], bloodTypeSchema["required"])

            print "\t\t\t Each schema property entry has required title,description,type"
            props = schema_data["properties"]
            for key, value in props.items():
                self.assertIn("description", value)
                self.assertIn("title", value)
                self.assertIn("type", value)
                self.assertEquals("string", value["type"])
    def test_modify_blood_type(self):
        """
        Modify an exsiting blood type and check that the blood type has been modified correctly 
        """
        print "("+self.test_modify_blood_type.__name__+")", self.test_modify_blood_type.__doc__

        resp = self.client.put(self.url,
                               data=json.dumps(self.blood_type_3),
                               headers={"Content-Type": JSON})
        print "\tAsserting that correctly modified blood tyoe returns status code 204"
        
        self.assertEquals(resp.status_code, 204)

        print "\tChecking that the blood type was actually modified"        
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 200)
        data = json.loads(resp2.data)
        print "\t\tAsserting that name was modified"
        self.assertEquals(data["name"], self.blood_type_3["name"])
              
    def test_modify_wrong_body(self):
        """
        Try to modify a blood type with wrong body
        """
        print "("+self.test_modify_wrong_body.__name__+")", self.test_modify_wrong_body.__doc__
        
        resp = self.client.put(self.url,
                               data=json.dumps(self.blood_type_2),
                               headers={"Content-Type": JSON})
        self.assertEquals(resp.status_code, 500)
    def test_modify_unexisting_blood_type(self):
        """
        Trying to modify a non existent blood type
        """
        print "("+self.test_modify_unexisting_blood_type.__name__+")", self.test_modify_unexisting_blood_type.__doc__
        resp = self.client.put(self.url_unexisting_item,
                                data=json.dumps(self.blood_type_1),
                                headers={"Content-Type": JSON})
        print "\tAsserting that response returns status code 404"                       
        self.assertEquals(resp.status_code, 404)
    def test_delete_blood_type(self):
        """
        Checks that Delete Blood type return correct status code if correctly delete
        """
        print "("+self.test_delete_blood_type.__name__+")", self.test_delete_blood_type.__doc__
        resp = self.client.delete(self.url)

        print "\tAsserting that response returns status code 204"
        self.assertEquals(resp.status_code, 204)
        print "\tChecking that the blood type was actually deleted"
        print "\tAsserting that trying to load the deleted item returns 404"
        resp2 = self.client.get(self.url)
        self.assertEquals(resp2.status_code, 404)

    
    def test_delete_wrong_url(self):
        """
        Checking that that Delete Blood type returns correct status code if given a wrong address
        """
        print "("+self.test_delete_wrong_url.__name__+")", self.test_delete_wrong_url.__doc__
        resp = self.client.delete(self.url_wrong)
        self.assertEquals(resp.status_code, 404)  
         
class BloodDonorTestCase(ResourcesAPITestCase):
    donor_1_request={
        "firstname": "Roope",
        "telephone": "+35854611111"
    }

    donor_2_request={
        "someName": "Roope",
        "someTelephone": "+35854611111"
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
        wrong URL
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
        Checking that GET Blood Donor return correct status code and MASON hypermedia format
        """

        print "("+self.test_get_blood_donor.__name__+")", self.test_get_blood_donor.__doc__
        with resources.app.test_client() as client:
            resp = client.get(self.url)
            print "\tAsserting that response has status code 200"
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
            all_donations=controls["bloodalert:blood-donor-history-list"]
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
            print "\t\t has method and method=DELETE"
            self.assertEquals(delete_ctrl["method"],"DELETE")

            print "\tAsserting that @controls has bloodalert:edit and in correct format"
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
            
            print "\t\thas schema and schema has all required atttributes type, properties, required"

            schema_data = edit_donor_ctrl["schema"]
            bloodDonorSchema=resources.BloodAlertObject()._blood_donor_schema(edit=True)
            print "\t\t\tschema has type"
            self.assertIn("type", schema_data)
            print "\t\t\tschema has properties and in correct format with all attributes"
            self.assertIn("properties", schema_data)
            self.assertEquals(schema_data["properties"], bloodDonorSchema["properties"])
            print "\t\t\tschema has required"
            self.assertIn("required", schema_data)
            self.assertEquals(schema_data["required"], bloodDonorSchema["required"])

            print "\t\t\t Each schema property entry has required title,description,type"
            props = schema_data["properties"]
            for key, value in props.items():
                self.assertIn("description", value)
                self.assertIn("title", value)
                self.assertIn("type", value)
                self.assertEquals("string", value["type"])
            
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
        self.assertEquals(resp.status_code, 500)
        

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
        Checks that GET Blood donors return correct status code and data format
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

        print "\tAsserting that @controls has bloodalert:blood-types-all and in correct format"
        self.assertIn("bloodalert:blood-types-all", controls)
        blood_types_all=controls["bloodalert:blood-types-all"]
        print "\t\t has title"
        self.assertIn("title", blood_types_all)
        print "\t\t has href and href={}".format("/bloodalert/bloodtypes/")
        self.assertIn("href", blood_types_all)
        self.assertEquals(blood_types_all["href"], "/bloodalert/bloodtypes/")

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
        bloodDonorSchema=resources.BloodAlertObject()._blood_donor_schema(edit=False)
        print "\t\t\tschema has type"
        self.assertIn("type", schema_data)
        print "\t\t\tschema has properties and in correct format with all attributes"
        self.assertIn("properties", schema_data)
        self.assertEquals(schema_data["properties"], bloodDonorSchema["properties"])
        print "\t\t\tschema has required"
        self.assertIn("required", schema_data)
        self.assertEquals(schema_data["required"], bloodDonorSchema["required"])
        
        print "\t\t\tEach schema property entry has required title,description,type"
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

class BloodBankBloodLevelsTestCase(ResourcesAPITestCase):
    
    def setUp(self):
        
        super(BloodBankBloodLevelsTestCase, self).setUp()
        self.url = resources.api.url_for(resources.BloodBankBloodLevels,
                                         bloodBankId="bbank-1",
                                         _external=False)
        self.url_wrong = resources.api.url_for(resources.BloodBankBloodLevels,
                                               bloodBankId="bbank-789",
                                               _external=False)

    def test_url(self):
        """
        Checks that the URL points to the right resource
        """        
        _url = "/bloodalert/bloodbanks/bbank-1/bloodlevels/"
        print "("+self.test_url.__name__+")", self.test_url.__doc__
        with resources.app.test_request_context(_url):
            rule = flask.request.url_rule
            view_point = resources.app.view_functions[rule.endpoint].view_class
            self.assertEquals(view_point, resources.BloodBankBloodLevels)
    
    def test_wrong_url(self):
        """
        Checks that GET Blood Bank Blood levels return correct status code if given a
        wrong URL
        """
        print "("+self.test_wrong_url.__name__+")", self.test_wrong_url.__doc__
        resp = self.client.get(self.url_wrong)
        self.assertEquals(resp.status_code, 404)      
    def test_get_blood_bank_blood_level_correct_status_code_headers(self):
        """
        Checks that GET Blood bank blood level return correct status code and content type in headers
        """
        print "("+self.test_get_blood_bank_blood_level_correct_status_code_headers.__name__+")", self.test_get_blood_bank_blood_level_correct_status_code_headers.__doc__        
        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)
        print "\tAsserting that response header has Content-Type:{}".format(MASON_JSON)
        self.assertEquals(resp.headers.get("Content-Type",None),
                          "{};{}".format(MASON_JSON, BLOODALERT_BLOOD_BANK_PROFILE))
    def test_get_blood_bank_blood_level(self):
        """
        Checking that GET Blood bank blood level return correct status code and MASON hypermedia format
        """

        print "("+self.test_get_blood_bank_blood_level.__name__+")", self.test_get_blood_bank_blood_level.__doc__
        
        resp = self.client.get(self.url)
        print "\tAsserting that response has status code 200"
        self.assertEquals(resp.status_code, 200)

        print "\tChecking correctness of hypermedia format"
        data = json.loads(resp.data)      
       
        controls = data["@controls"]
        print "\tAsserting that @controls has self link relation"
        self.assertIn("self", controls)
        self.assertIn("href", controls["self"])
        self.assertEquals(controls["self"]["href"], self.url)

        print "\tAsserting that @controls has parent and in correct format"
        self.assertIn("parent", controls)
        parent=controls["parent"]
        print "\t\t has title"
        self.assertIn("title", parent)
        parent_url=resources.api.url_for(resources.BloodBank,bloodBankId="bbank-1",_external=False)
        print "\t\t has href and href={}".format(parent_url)
        self.assertIn("href", parent)
        self.assertEquals(parent["href"], parent_url)

        
        
        print "\tAsserting that response items and in correct format"
        items = data["items"]       
        for item in items:
            self.assertIn("bloodTypeName", item)
            self.assertIn("amount", item)
            
            self.assertIn("@controls", item)         
            self.assertIn("profile", item["@controls"])
            self.assertEquals(item["@controls"]["profile"]["href"], BLOODALERT_BLOOD_BANK_PROFILE)
            self.assertIn("bloodType", item["@controls"])
            self.assertEquals(item["@controls"]["bloodType"]["href"],resources.api.url_for(resources.BloodType,bloodTypeId=item["bloodTypeId"],_external=False))        




if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()

    