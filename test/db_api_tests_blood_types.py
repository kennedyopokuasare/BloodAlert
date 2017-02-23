'''
Created on 21.02.2017

Unittest for testing the Database Blood Types Database API

@author: asare
'''

import sqlite3
import unittest

from src import database


DB_PATH = 'db/bloodAlert_test.db'
ENGINE = database.Engine(DB_PATH)


BLOOD_TYPE_EMPTY = ""
BLOOD_TYPE_ID="btype-1"
BLODD_TYPE_ID2="btype-3"
EXISTING_BLOOD_TYPE_NAME = "O+"
EXISTING_BLOOD_TYPE_ID = "btype-1"
NEW_BLOOD_TYPE = "ANOTHER BLOOD TYPE"
NUMBER_OF_ENTRIES = 8
BLOOD_TYPE_1 = {
            'bloodTypeId': BLOOD_TYPE_ID, 'name': EXISTING_BLOOD_TYPE_NAME,
        }
BLOOD_TYPE_2= {
            'bloodTypeId': BLOOD_TYPE_ID, 'name':NEW_BLOOD_TYPE,
        }


class BloodTypesDBAPITestCase(unittest.TestCase):

    # Unittest setup methods.. imported from Exercese codes

    '''
    Test cases for the Blood Types related methods.
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

    def test_blood_Types_table_created(self):
        '''
        Checks that the blood_types table is created and populated contains 8 Blood Types. 
        '''
        print '\n(' + self.test_blood_Types_table_created.__name__ + ')', \
            self.test_blood_Types_table_created.__doc__

        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Blood_Types'
        con = self.connection.con

        with con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            print('\tQuerying the database with: ' + query)

            cur.execute(query)
            print('\tGetting results from query')
            bloodTypes = cur.fetchall()
            # Assert
            print('\tAsserting that Blood_Type table has ' +
                  str(NUMBER_OF_ENTRIES) + ' entries: ')
            self.assertEquals(len(bloodTypes), NUMBER_OF_ENTRIES)

    def test_create_same_bloodType_exists(self):
        '''
        Test that the Blood_Type table ensures UNIQUE blood_type name
        '''
        print '\n(' + self.test_create_same_bloodType_exists.__name__ + ')', \
            self.test_create_same_bloodType_exists.__doc__

        print '\tCreating Blood Type with existing name '
        with self.assertRaises(sqlite3.IntegrityError):
            print '\tCreating new Blood Type with existing name ' + EXISTING_BLOOD_TYPE_NAME
            print '\tAsserting that Database throws an error about UNIQUE constraints'
            self.connection.create_blood_type(EXISTING_BLOOD_TYPE_NAME)

    def test_create_blood_type_name_empty(self):
        '''
        Test that an empty Blood Type name is not entered into database
        '''
        print '\n(' + self.test_create_blood_type_name_empty.__name__ + ')', \
            self.test_create_blood_type_name_empty.__doc__

        with self.assertRaises(ValueError):
            print '\tCreating new Blood Type with empty name '
            print '\tAsserting that create_blood_type method raises \
                     ValueError Exception (Name cannot be empty)'
            self.connection.create_blood_type(BLOOD_TYPE_EMPTY)

    def test_blood_type_id_malformed(self):
        '''
        Test that all methods checks for malformed bloodType Id
        Note that blood type id is for the format btype-\d{1,3}
        '''
        print '\n(' + self.test_blood_type_id_malformed.__name__ + ')', \
              self.test_blood_type_id_malformed.__doc__

        print '\tTesting get_blood_type method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood type id argument'
            self.connection.get_blood_type('1')

        print '\tTesting modify_blood_type method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood type id argument'
            self.connection.modify_blood_type('1')

        print '\tTesting delete_blood_type method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood type id argument'
            self.connection.delete_blood_type('1')


    # Test cases for CRUD
    def test_get_blood_methods_load_data(self):
        '''
        Test that all get methods loads blood type(s) from database successfully
        '''
        print '\n(' + self.test_get_blood_methods_load_data.__name__ + ')', \
            self.test_get_blood_methods_load_data.__doc__
        
        print '\ttesting get_blood_type method'
        bloodType=self.connection.get_blood_type(BLOOD_TYPE_ID)
        print '\t\tAsserting that method returns dictionary which has entry: '+str(BLOOD_TYPE_1)
        self.assertDictContainsSubset(bloodType, BLOOD_TYPE_1)
        print '\ttesting get_blood_types method'
        bloodTypes=self.connection.get_blood_types()
        
        print '\t\tAsserting that method returns a list that has entries '
        self.assertTrue(len(bloodTypes)>0)
        print '\t\tAsserting that method returns a list which has disctionaries of correct formats'
        for  bt in bloodTypes:
            if bt['bloodTypeId']==BLOOD_TYPE_ID:
                self.assertEquals(len(bt), 2)
                self.assertDictContainsSubset(bt, BLOOD_TYPE_1)
       
    def test_modify_blood_type(self):
        '''
        Test that blood type is modified 
        '''  
        print '\n(' + self.test_modify_blood_type.__name__ + ')', \
            self.test_modify_blood_type.__doc__  

        print '\tModifying existing blood type '+EXISTING_BLOOD_TYPE_NAME
        bloodTypeId=self.connection.modify_blood_type(EXISTING_BLOOD_TYPE_ID ,NEW_BLOOD_TYPE)
        print '\tAsserting that blood type is modified'
        self.assertEqual(bloodTypeId,EXISTING_BLOOD_TYPE_ID)
        print '\tAsserting that name column of blood type was actually modified'
        bloodType=self.connection.get_blood_type(EXISTING_BLOOD_TYPE_ID)
        self.assertDictContainsSubset(bloodType,BLOOD_TYPE_2)

    def test_create_blood_type(self):
        '''
        Test that blood type is created 
        '''  
        print '\n(' + self.test_create_blood_type.__name__ + ')', \
            self.test_create_blood_type.__doc__  
        
        print'\tCreating a new blood type '+NEW_BLOOD_TYPE
        bloodTypeId=self.connection.create_blood_type(NEW_BLOOD_TYPE)
        print'+tAsserting that returned bloodTypeId is not non'
        self.assertIsNotNone (bloodTypeId)

    def test_delete_blood_Type(self):
        '''
        Test that blood type is deleted 
        '''  
        print '\n(' + self.test_delete_blood_Type.__name__ + ')', \
            self.test_delete_blood_Type.__doc__  
        
        print '\tDeleting Blood Type '+str(BLOOD_TYPE_1)
        print '\Asserting that  delete_blood_type method returns true'
        results= self.connection.delete_blood_type(BLOOD_TYPE_ID)
        self.assertTrue(results)
        print '\Asserting that  blood type is really deleted'
        self.assertIsNone(self.connection.get_blood_type(BLOOD_TYPE_ID))
       



if __name__ == '__main__':
    print 'Start running Blood Types tests'
    unittest.main()
