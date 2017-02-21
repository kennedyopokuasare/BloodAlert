'''
Created on 21.02.2017

Unittest for testing the Database Blood Banks Database API

@author: asare, arash, anastasiia
'''

import sqlite3
import unittest

from src import database

DB_PATH = 'db/bloodAlert_test.db'
ENGINE = database.Engine(DB_PATH)

class BloodBanksDBAPITestCase(unittest.TestCase):
 
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
    def test_blood_bank_id_malformed(self):
        '''
            Test that blood bank id passed is of the format bbank-\d{1,3}
        '''
        print '\n(' + self.test_blood_bank_id_malformed.__name__ + ')', \
              self.test_blood_bank_id_malformed.__doc__
        
        print '\tTesting get_blood_bank method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood type id argument'
            self.connection.get_blood_bank('1')
        
        print '\tTesting delete_blood_bank method'


        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood type id argument'
            self.connection.delete_blood_bank('1')

        print '\tTesting modify_blood_bank method'
        
        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueException with malformed blood type id argument'
            self.connection.modify_blood_bank('1')
            

