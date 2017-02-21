'''
Created on 21.02.2017

Unittest for testing the Database Blood Types Database API

@author: asare
'''

import sqlite3, unittest

from  src import database


DB_PATH = 'db/bloodAlert_test.db'
ENGINE = database.Engine(DB_PATH)



BLOOD_TYPE_EMPTY=""
EXISTING_BLOOD_TYPE_NAME="A+"
EXISTING_BLOOD_TYPE_ID="btype-1"
NEW_BLOOD_TYPE="ANOTHER BLOOD TYPE"
NUMBER_OF_ENTRIES=8


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
        print '\n('+self.test_blood_Types_table_created.__name__+')', \
                  self.test_blood_Types_table_created.__doc__

        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM Blood_Types'
        con = self.connection.con

        with con:
          
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            print('\tQuerying the database with: '+query)
          
            cur.execute(query)
            print('\tGetting results from query')
            bloodTypes = cur.fetchall()
            #Assert
            print('\tAsserting that Blood_Type table has '+str(NUMBER_OF_ENTRIES)+' entries: ')
            self.assertEquals(len(bloodTypes), NUMBER_OF_ENTRIES)
    
    def test_create_same_bloodType_exists(self):
        '''
            Test that the Blood_Type table ensures UNIQUE blood_type name
        '''
        print '\n('+self.test_create_same_bloodType_exists.__name__+')', \
                  self.test_create_same_bloodType_exists.__doc__
        
        print '\tCreating Blood Type with empty (string) name '
        with self.assertRaises(sqlite3.IntegrityError):
            print '\tCreating new Blood Type with existing name '+EXISTING_BLOOD_TYPE_NAME
            print '\tAsserting that Database throws an error about UNIQUE constraints'
            self.connection.create_blood_type(EXISTING_BLOOD_TYPE_NAME)

    def test_create_blood_type_name_empty(self):
        '''
            Test that an empty Blood Type name is not entered into database
        '''  
        print '\n('+self.test_create_blood_type_name_empty.__name__+')', \
                  self.test_create_blood_type_name_empty.__doc__
    
        with self.assertRaises(ValueError):
            print '\tCreating new Blood Type with emoty name '
            print '\tAsserting that create_blood_type method raises ValueError Exception (Name cannot be empty)'
            self.connection.create_blood_type(BLOOD_TYPE_EMPTY)
        
    
    
    def test_blood_type_id_malformed(self):

        '''
        Test that all methods checks for malformed bloodType Id
        Note that blood type id is for the format btype-\d{1,3}
        '''
        print '('+self.test_blood_type_id_malformed.__name__+')', \
              self.test_blood_type_id_malformed.__doc__
       
        print 'Testing get_blood_type method'

        with self.assertRaises(ValueError):
            print 'Asserting that method throw ValueException with malformed blood type id argument'
            self.connection.get_blood_type('1')

        print '`Testing modify_blood_type method'

        with self.assertRaises(ValueError):
            print 'Asserting that method throw ValueException with malformed blood type id argument'
            self.connection.modify_blood_type('1')

        print '`Testing delete_blood_type method'

        with self.assertRaises(ValueError):
            print 'Asserting that method throw ValueException with malformed blood type id argument'
            self.connection.delete_blood_type('1')
        
   


if __name__ == '__main__':
    print 'Start running message tests'
    unittest.main()
