'''
Created on 23.02.2017

Unittest for testing the Database Blood Donors Database API

@author: asare, arash, anastasiia
'''

import sqlite3
import unittest

from src import database

DB_PATH = 'db/bloodAlert_test.db'
ENGINE = database.Engine(DB_PATH)

NUMBER_OF_ENTRIES = 8
EXISTING_EMAIL = "VicGugo@oulu.fi"
FIRSTNAME = "Anas"
FAMILY_NAME = "Boro"
BLOOD_TYPE_Id = "btype-1"
BLOOD_Donor_Id = "bdonor-1"
DATE = "12-08-2015"
DATE_WRONG_FORMAT = "134-9 7"
GENDER = "Female"
Gender_WRONG_FORMAT = "--Male"

CITY = "Jyvaskyla"
TELEPHONE = "+358303833374"
EMAIL = "jyvaskyla@gmail.com"

BLOOD_DONOR_1 = {
    'donorId': BLOOD_Donor_Id,
    'firstname': "Anna", 'familyName': "Bord",
    'birthDate': '30-12-1986', 'gender': 'Female',
    'bloodTypeId': 'btype-1', 'telephone': '+348416754234',
    'city': 'Oulu', 'address': 'Linnanmaa', 'email': 'AnB@oulu.fi'
}


class BloodDonorsDBAPITestCase(unittest.TestCase):

    # Unittest setup methods.. imported from Exercese codes

    '''
    Test cases for the Blood Donors related methods.
    '''
    @classmethod
    def setUpClass(cls):
        ''' Creates the database structure. Removes first any preexisting
            database file
        '''
        print "Testing ", cls.__name__
        ENGINE.remove_database()
        ENGINE.create_tables()

    @classmethod
    def tearDownClass(cls):
        '''Remove the testing database'''
        print "Testing ENDED for ", cls.__name__
        ENGINE.remove_database()

    def setUp(self):
        '''
        Populates the database
        '''
        ENGINE.populate_tables()
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

 # Test cases for preditable errors
    def test_blood_donors_table_created(self):
        '''
        Checks that the blood_donors table is created and populated contains 8 entries. 
        '''
        print '\n(' + self.test_blood_donors_table_created.__name__ + ')', \
            self.test_blood_donors_table_created.__doc__

        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM blood_donors'
        con = self.connection.con

        with con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            print('\tQuerying the database with: ' + query)

            cur.execute(query)
            print('\tGetting results from query')
            bloodBanks = cur.fetchall()
            # Assert
            print('\tAsserting that blood_donors table has ' +
                  str(NUMBER_OF_ENTRIES) + ' entries: ')
            self.assertEquals(len(bloodBanks), NUMBER_OF_ENTRIES)

    def test_blood_donors_id_malformed(self):
        '''
        Test that blood donor id passed to method(s) is of the format bdonor-\d{1,3}
        '''
        print '\n(' + self.test_blood_donors_id_malformed.__name__ + ')', \
              self.test_blood_donors_id_malformed.__doc__

        print '\tTesting get_blood_donor method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood donor id argument'
            self.connection.get_blood_donor('1')

        print '\tTesting delete_blood_donor method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood donor id argument'
            self.connection.delete_blood_donor('1')

        print '\tTesting modify_blood_donor method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood donor id argument'
            self.connection.modify_blood_donor('1')

    def test_blood_donors_ensures_unique_emails(self):
        '''
        Test that blood donors with same  emails cannot exists
        '''
        print '\n(' + self.test_blood_donors_ensures_unique_emails.__name__ + ')', \
              self.test_blood_donors_ensures_unique_emails.__doc__
        with self.assertRaises(sqlite3.IntegrityError):
            print '\tAsserting that creating blood Donor with existing Blood Donor email ' + EXISTING_EMAIL + ' throws sqlite3.IntegrityError'
            self.connection.create_blood_donor(FIRSTNAME, FAMILY_NAME, TELEPHONE,
                                               EXISTING_EMAIL, BLOOD_TYPE_Id, DATE, GENDER)

    def test_blood_donor_modify_parameters_malformed(self):
        '''
        Test that  modify_blood_donor method checks for welformed birthDate, bloodTypeId, GENDER
        '''
        print '\n(' + self.test_blood_donor_modify_parameters_malformed.__name__ + ')', \
              self.test_blood_donor_modify_parameters_malformed.__doc__

        with self.assertRaises(ValueError):
            print '\tAsserting that modifying blood Donor wrongly formated date ' + DATE_WRONG_FORMAT + ' throws ValueError'
            self.connection.modify_blood_donor(
                BLOOD_Donor_Id, birthDate=DATE_WRONG_FORMAT)

        with self.assertRaises(ValueError):
            print '\tAsserting that creating blood Donor wrongly formated gender ' + Gender_WRONG_FORMAT + ' throws ValueError'
            self.connection.modify_blood_donor(
                BLOOD_Donor_Id, gender=Gender_WRONG_FORMAT)

        with self.assertRaises(ValueError):
            print '\tAsserting that creating blood Donor wrongly formated bloodTypeId ' + str(1) + ' throws ValueError'
            self.connection.modify_blood_donor(BLOOD_Donor_Id, bloodTypeId=1)

    def test_blood_donor_create_parameters_malformed(self):
        '''
        Test that  create_blood_donor method checks for welformed birthDate, bloodTypeId, GENDER
        '''
        print '\n(' + self.test_blood_donor_create_parameters_malformed.__name__ + ')', \
              self.test_blood_donor_create_parameters_malformed.__doc__

        with self.assertRaises(ValueError):
            print '\tAsserting that creating blood Donor wrongly formated date ' + DATE_WRONG_FORMAT + ' throws ValueError'
            self.connection.create_blood_donor(FIRSTNAME, FAMILY_NAME, TELEPHONE,
                                               EXISTING_EMAIL, BLOOD_TYPE_Id, DATE_WRONG_FORMAT, GENDER)
        with self.assertRaises(ValueError):
            print '\tAsserting that creating blood Donor wrongly formated gender ' + Gender_WRONG_FORMAT + ' throws ValueError'
            self.connection.create_blood_donor(FIRSTNAME, FAMILY_NAME, TELEPHONE,
                                               EXISTING_EMAIL, BLOOD_TYPE_Id, DATE, Gender_WRONG_FORMAT)

        with self.assertRaises(ValueError):
            print '\tAsserting that creating blood Donor wrongly formated bloodTypeId ' + str(1) + ' throws ValueError'
            self.connection.create_blood_donor(FIRSTNAME, FAMILY_NAME, TELEPHONE,
                                               EXISTING_EMAIL, 1, DATE, GENDER)
# Test cases for CRUD

    def test_delete_blood_donor(self):
        '''
        Test that blood donor is deleted
        '''
        print '\n(' + self.test_delete_blood_donor.__name__ + ')', \
              self.test_delete_blood_donor.__doc__

        print '\tDeleting Blood Donor ' + str(BLOOD_Donor_Id)
        print '\Asserting that  delete_blood_donor method returns true'
        results = self.connection.delete_blood_donor(BLOOD_Donor_Id)
        self.assertTrue(results)
        print '\Asserting that the blood donor is really deleted'
        self.assertIsNone(self.connection.get_blood_donor(BLOOD_Donor_Id))

    def test_blood_donor_load(self):
        '''
        Test that get_blood_donor and get_blood_donors methos load data
        '''
        print '\n(' + self.test_blood_donor_load.__name__ + ')', \
              self.test_blood_donor_load.__doc__

        print '\ttesting get_blood_donor method'
        bloodDonor = self.connection.get_blood_donor(BLOOD_Donor_Id)
        print '\t\tAsserting that method returns dictionary which has entry: ' + str(BLOOD_Donor_Id)
        self.assertDictContainsSubset(bloodDonor, BLOOD_DONOR_1)

        print '\ttesting get_blood_donors method'
        bloodDonors = self.connection.get_blood_donors()

        print '\t\tAsserting that method returns a list that has entries '
        self.assertTrue(len(bloodDonor) > 0)
        print '\t\tAsserting that method returns a list which has disctionaries of correct formats'
        for bd in bloodDonors:
            if bd['donorId'] == BLOOD_Donor_Id:
                self.assertEquals(len(bd), 10)
                self.assertDictContainsSubset(bd, BLOOD_DONOR_1)

    def test_create_blood_donor(self):
        '''
        Test that blood donor is created
        '''
        print '\n(' + self.test_create_blood_donor.__name__ + ')', \
              self.test_create_blood_donor.__doc__

        print '\tAsserting that blood bank is created without address, latitude and longitude'
        res1 = self.connection.create_blood_donor(
            FIRSTNAME,FAMILY_NAME, TELEPHONE, EMAIL,BLOOD_TYPE_Id,DATE,GENDER)
        self.assertIsNotNone(res1)
        

    def test_modify_blood_donor(self):
        '''
        Test that blood donor is modified
        '''
        print '\n(' + self.test_modify_blood_donor.__name__ + ')', \
            self.test_modify_blood_donor.__doc__

        print '\tModifying existing blood donor. Updating telephone number to ' + TELEPHONE
        bloodBank = self.connection.modify_blood_donor(
            BLOOD_Donor_Id, telephone=TELEPHONE)
        print '\tAsserting that blood donor is modified'
        self.assertEqual(bloodBank, BLOOD_Donor_Id)
        print '\tAsserting that telephone column of blood donor was actually modified'
        bloodDonor = self.connection.get_blood_donor(BLOOD_Donor_Id)
        self.assertEqual(bloodDonor["telephone"], TELEPHONE)


if __name__ == '__main__':
    print 'Start running Blood Banks tests'
    unittest.main()
