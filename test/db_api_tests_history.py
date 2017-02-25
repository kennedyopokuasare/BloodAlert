'''
Created on 25.02.2017

Unittest for testing the History Database API

@author: asare, arash, anastasiia
'''

import sqlite3
import unittest

from src import database

DB_PATH = 'db/bloodAlert_test.db'
ENGINE = database.Engine(DB_PATH)

NUMBER_OF_ENTRIES=15
HISTORY_ID='history-1'
BLOOD_BANK_ID = "bbank-2"
BLOOD_TYPE_ID="btype-1"
AMOUNT=200
DONOR_ID='bdonor-1'
DONOR_ID2='bdonor-3'

HISTORY_1={
    'historyId':'history-2',
    'donorId':'bdonor-2',
    'bloodTypeId':'btype-2',
    'bloodBankId':BLOOD_BANK_ID,
    'amount':300,
    'timeStamp':'2016-10-08 13:54:12',
    'tag':'DONATION'
}

HISTORY_2={
    'historyId':'history-2',
    'donorId':'bdonor-2',
    'bloodTypeId':'btype-2',
    'bloodBankId':BLOOD_BANK_ID,
    'amount':300,
    'timeStamp':'2016-10-08 13:54:12',
    'tag':'DONATION'
}

class HistoryDBAPITestCase(unittest.TestCase):

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
    def test_history_table_creted(self):

        '''
        Checks that the History table is created and populated contains 15 entries. 
        '''
        print '\n(' + self.test_history_table_creted.__name__ + ')', \
            self.test_history_table_creted.__doc__

        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM History'
        con = self.connection.con

        with con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(keys_on)
            print('\tQuerying the database with: ' + query)

            cur.execute(query)
            print('\tGetting results from query')
            history = cur.fetchall()
            # Assert
            print('\tAsserting that History table has ' +
                  str(NUMBER_OF_ENTRIES) + ' entries: ')
            self.assertEquals(len(history), NUMBER_OF_ENTRIES)
    def test_history_id_malformed(self):
        '''
        Test that history id passed to method(s) is of the format history-\d{1,3}
        '''
        print '\n(' + self.test_history_id_malformed.__name__ + ')', \
              self.test_history_id_malformed.__doc__

        print '\tTesting get_history'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueError with malformed history id argument 1'
            self.connection.get_history('1')

        print '\tTesting delete_history method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueError with malformed history id argument 1'
            self.connection.delete_history('1')

        print '\tTesting modify_history method'

        with self.assertRaises(ValueError):
            print '\tAsserting that method throw ValueError with malformed history id argument 1'
            self.connection.modify_history('1')
    def test_history_create_parameters_malformed(self):
        '''
        Test that  create_history method checks for well formed  bloodTypeId, bloodBankId, amount, donorId, tag
        '''
        print '\n(' + self.test_history_create_parameters_malformed.__name__ + ')', \
              self.test_history_create_parameters_malformed.__doc__

        with self.assertRaises(ValueError):
            print '\tAsserting that creating history with wrongly formated bloodTypeId 1 throws ValueError'
            self.connection.create_history(1,BLOOD_BANK_ID,AMOUNT)
        with self.assertRaises(ValueError):
            print '\tAsserting that creating history with wrongly formated bloodBankId throws ValueError'
            self.connection.create_history(BLOOD_TYPE_ID, 1,AMOUNT)

        with self.assertRaises(ValueError):
            print '\tAsserting that creating history with wrongly formated amount 12&0=+ throws ValueError'
            self.connection.create_history(BLOOD_TYPE_ID, BLOOD_BANK_ID,str('12&0=+'))
        with self.assertRaises(ValueError):
            print '\tAsserting that creating history with wrongly formated donor id 1 throws ValueError'
            self.connection.create_history(BLOOD_TYPE_ID, BLOOD_BANK_ID,AMOUNT,donorId=1)
        with self.assertRaises(ValueError):
            print '\tAsserting that creating history with wrongly formated tag NOTHING throws ValueError'
            self.connection.create_history(BLOOD_TYPE_ID, BLOOD_BANK_ID,AMOUNT,tag='NOTHING')


    def test_history_modify_parameters_malformed(self):
        '''
        Test that  modify_history method checks for well formed  bloodTypeId, bloodBankId, amount, donorId, tag
        '''    
        print '\n(' + self.test_history_modify_parameters_malformed.__name__ + ')', \
              self.test_history_modify_parameters_malformed.__doc__

    

        with self.assertRaises(ValueError):
            print '\tAsserting that modifying history with wrongly formated bloodTypeId'+str(1)+' throws ValueError'
            self.connection.modify_history(
                HISTORY_ID, bloodBankId=1)

        with self.assertRaises(ValueError):
            print '\tAsserting that modifying history with wrongly formated  bloodBankId ' + str(1) + ' throws ValueError'
            self.connection.modify_history(HISTORY_ID, bloodBankId=1)
            
        with self.assertRaises(ValueError):
            print '\tAsserting that modifying history with wrongly formated amount ' + str('123&+1==') + ' throws ValueError'
            self.connection.modify_history(HISTORY_ID, amount=str('123&+1==') )
        with self.assertRaises(ValueError):
            print '\tAsserting that modifying history with wrongly formated donorId ' + str(1)+ ' throws ValueError'
            self.connection.modify_history(HISTORY_ID, donorId=1)
        with self.assertRaises(ValueError):
            print '\tAsserting that modifying history with wrongly formated tag ' + str('123&+1==') + ' throws ValueError'
            self.connection.modify_history(HISTORY_ID, tag=str('123&+1==') )

 # Test cases for CRUD
    def test_history_load(self):
        '''
        Test that get_blood_donor_histories and get_blood_bank_histories loads data
        '''
        print '\n(' + self.test_history_load.__name__ + ')', \
              self.test_history_load.__doc__

        print '\ttesting get_blood_donor_histories method'
        history = self.connection.get_blood_bank_histories(BLOOD_BANK_ID)
        print '\t\tAsserting that method method returns a list that has entries'
        self.assertTrue(len(history) > 0)
        print '\t\tAsserting that method returns a list which has disctionaries of correct formats'
        for entry in history:
            if entry['historyId'] == HISTORY_2:
                self.assertEquals(len(entry), 7)
                self.assertDictContainsSubset(entry, HISTORY_2)

        print '\ttesting get_blood_donor_histories method'
        history2 = self.connection.get_blood_donor_histories(DONOR_ID2)
        print '\t\tAsserting that method returns a list that has entries '
        self.assertTrue(len(history2) > 0)
        for entry in history:
            if entry['historyId'] == HISTORY_1:
                self.assertEquals(len(entry), 7)
                self.assertDictContainsSubset(entry, HISTORY_1)

    def test_create_history(self):
        '''
        Test that history is created
        '''
        print '\n(' + self.test_create_history.__name__ + ')', \
              self.test_create_history.__doc__

        print '\tAsserting that is created '
        res1 = self.connection.create_history(BLOOD_TYPE_ID,BLOOD_BANK_ID,AMOUNT,DONOR_ID)
        self.assertIsNotNone(res1)

    def test_delete_history(self):
        '''
        Test that history is deleted
        '''
        print '\n(' + self.test_delete_history.__name__ + ')', \
              self.test_delete_history.__doc__

       
        print '\Asserting that  delete_history method returns true'
        results = self.connection.delete_history(HISTORY_ID)
        self.assertTrue(results)
        print '\Asserting that the history is really deleted'
        self.assertIsNone(self.connection.get_history(HISTORY_ID))

    def test_modify_history(self):
        '''
        Test that History is modified
        '''
        print '\n(' + self.test_modify_history.__name__ + ')', \
            self.test_modify_history.__doc__

        print '\tModifying existing history. Updating amount of blood to number to ' + str(300)
        history = self.connection.modify_history(
            HISTORY_ID, amount=300,bloodBankId=BLOOD_BANK_ID)
        print '\tAsserting that blood donor is modified'
        self.assertEqual(history, HISTORY_ID)
        print '\tAsserting that amount column of history was actually modified'
        history = self.connection.get_history(HISTORY_ID)
        self.assertEqual(history["amount"], 300)


if __name__ == '__main__':
    print 'Start running Blood Types tests'
    unittest.main()