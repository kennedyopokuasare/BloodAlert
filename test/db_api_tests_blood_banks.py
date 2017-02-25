'''
Created on 21.02.2017

Unittest for testing the  Blood Banks Database API

@author: asare, arash, anastasiia
'''

import sqlite3
import unittest

from src import database

DB_PATH = 'db/bloodAlert_test.db'
ENGINE = database.Engine(DB_PATH)

NUMBER_OF_ENTRIES = 4
EXISTING_EMAIL = "OuluUniHospital@oulu.fi"
EXISTING_NAME = "Oulu University Hospital"
CITY = "Jyvaskyla"
TELEPHONE = "+358303833374"
EMAIL = "jyvaskyla@gmail.com"
EMAIL_2 = "juaben@gmail.com"
BLOOD_THRESHOLD = 20
NEW_NAME = "Juaben Hospital"
NEW_NAME_2 = "Kajaani Hospital"
ADDRESS = "Yliopistokatu 48"
LATITUDE = 1.93048308434
LONGITUDE = 1.2303033003

BLOOD_BANK_ID = "bbank-2"
BLOOD_BANK_1 = {
    'bloodBankId': BLOOD_BANK_ID, 'name': EXISTING_NAME,
    'address': 'Kajaanintie 50', 'city': 'Oulu',
    'telephone': '+358 8 3152011', 'email': 'OuluUniHospital@oulu.fi',
    'latitude': 65.007406, 'longitude': 25.517786,
    'threshold': 30
}


class BloodBanksDBAPITestCase(unittest.TestCase):

    # Unittest setup methods.. imported from Exercese codes

    '''
    Test cases for the Blood Banks related methods.
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
    def test_blood_banks_table_created(self):
        '''
        Checks that the blood_banks table is created and populated contains 4 entries. 
        '''
        print '\n(' + self.test_blood_banks_table_created.__name__ + ')', \
            self.test_blood_banks_table_created.__doc__

        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Blood_Banks'
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
            print('\tAsserting that Blood_Banks table has ' +
                  str(NUMBER_OF_ENTRIES) + ' entries: ')
            self.assertEquals(len(bloodBanks), NUMBER_OF_ENTRIES)

    def test_blood_banks_id_malformed(self):
        '''
        Test that blood bank id passed to method(s) is of the format bbank-\d{1,3}
        '''
        print '\n(' + self.test_blood_banks_id_malformed.__name__ + ')', \
              self.test_blood_banks_id_malformed.__doc__

        print '\tTesting get_blood_bank method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueError with malformed blood bank id argument'
            self.connection.get_blood_bank('1')

        print '\tTesting delete_blood_bank method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueError with malformed blood bank id argument'
            self.connection.delete_blood_bank('1')

        print '\tTesting modify_blood_bank method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueError with malformed Blood Bank id argument'
            self.connection.modify_blood_bank('1')

    def test_blood_banks_ensures_unique_names_and_emails(self):
        '''
        Test that blood banks with same name and/or emails cannot exists
        '''
        print '\n(' + self.test_blood_banks_ensures_unique_names_and_emails.__name__ + ')', \
              self.test_blood_banks_ensures_unique_names_and_emails.__doc__
        with self.assertRaises(sqlite3.IntegrityError):
            print '\tAsserting that creating blood Bank existing Blood bank name ' + EXISTING_NAME + ' throws sqlite3.IntegrityError'
            self.connection.create_blood_bank(
                EXISTING_NAME, CITY, TELEPHONE, EMAIL, BLOOD_THRESHOLD)
        with self.assertRaises(sqlite3.IntegrityError):
            print '\tAsserting that creating blood Bank existing Blood bank email ' + EXISTING_EMAIL + ' throws sqlite3.IntegrityError'
            self.connection.create_blood_bank(
                NEW_NAME, CITY, TELEPHONE, EXISTING_EMAIL, BLOOD_THRESHOLD)
 # Test cases for CRUD

    def test_create_blood_bank(self):
        '''
        Test that blood bank is create
        '''
        print '\n(' + self.test_create_blood_bank.__name__ + ')', \
              self.test_create_blood_bank.__doc__

        print '\tAsserting that blood bank is created without address, latitude and longitude'
        res1 = self.connection.create_blood_bank(
            NEW_NAME, CITY, TELEPHONE, EMAIL, BLOOD_THRESHOLD)
        self.assertIsNotNone(res1)
        print '\tAsserting that blood bank is created with address, latitude and longitude'
        res2 = self.connection.create_blood_bank(
            NEW_NAME_2, CITY, TELEPHONE, EMAIL_2, BLOOD_THRESHOLD, ADDRESS, LATITUDE, LATITUDE)
        self.assertIsNotNone(res2)

    def test_get_blood_bank_methods_load_data(self):
        '''
        Test that all get blood bank methods load data fron database 
        '''
        print '\n(' + self.test_get_blood_bank_methods_load_data.__name__ + ')', \
            self.test_get_blood_bank_methods_load_data.__doc__

        print '\ttesting get_blood_bank method'
        bloodBank = self.connection.get_blood_bank(BLOOD_BANK_ID)
        print '\t\tAsserting that method returns dictionary which has entry: ' + str(BLOOD_BANK_1)
        self.assertDictContainsSubset(bloodBank, BLOOD_BANK_1)

        print '\ttesting get_blood_banks method'
        bloodBanks = self.connection.get_blood_banks()

        print '\t\tAsserting that method returns a list that has entries '
        self.assertTrue(len(bloodBanks) > 0)
        print '\t\tAsserting that method returns a list which has disctionaries of correct formats'
        for bb in bloodBanks:
            if bb['bloodBankId'] == BLOOD_BANK_ID:
                self.assertEquals(len(bb), 9)
                self.assertDictContainsSubset(bb, BLOOD_BANK_1)

    def test_modify_blood_bank(self):
        '''
        Test that blood bank is modified
        '''
        print '\n(' + self.test_modify_blood_bank.__name__ + ')', \
            self.test_modify_blood_bank.__doc__  

        print '\tModifying existing blood bank '+EXISTING_NAME
        bloodBank=self.connection.modify_blood_bank(BLOOD_BANK_ID ,name= NEW_NAME,telephone=TELEPHONE)
        print '\tAsserting that blood bank is modified'
        self.assertEqual(bloodBank,BLOOD_BANK_ID)
        print '\tAsserting that name and telephone column of blood bank was actually modified'
        bloodBank=self.connection.get_blood_bank(BLOOD_BANK_ID)
        self.assertEqual(bloodBank["name"],NEW_NAME)
        self.assertEqual(bloodBank["telephone"],TELEPHONE)

    def test_delete_blood_bank(self):
        '''
        Test that blood bank is deleted 
        '''  
        print '\n(' + self.test_delete_blood_bank.__name__ + ')', \
            self.test_delete_blood_bank.__doc__  
        
        print '\tDeleting Blood Bank '+str(BLOOD_BANK_ID)
        print '\Asserting that  delete_blood_bank method returns true'
        results= self.connection.delete_blood_bank(BLOOD_BANK_ID)
        self.assertTrue(results)
        print '\Asserting that  blood bank is really deleted'
        self.assertIsNone(self.connection.get_blood_bank(BLOOD_BANK_ID))


if __name__ == '__main__':
    print 'Start running Blood Banks tests'
    unittest.main()
