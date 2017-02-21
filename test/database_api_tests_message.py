'''
Created on 13.02.2014
Modified on 01.02.2016
Database interface testing for all users related methods.

A Message object is a dictionary which contains the following keys:
      - messageid: id of the message (int)
      - title: message's title
      - body: message's TEXT
      - timestamp: UNIX timestamp (long integer) that specifies when the
                   message was created.
      - replyto: The id of the parent message. String with the format
                   msg-{id}. Its value can be None.
      - sender: The nickname of the message's creator
      - editor: The nickname of the message's editor.

A messages' list has the following format:
[{'messageid':'', 'title':'', 'timestamp':, 'sender':''},
 {'messageid':'', 'title':'', 'timestamp':, 'sender':''}]

@author: ivan
'''

import sqlite3, unittest

from bloodAlert import database

#Path to the database file, different from the deployment db
DB_PATH = 'db/forum_test.db'
ENGINE = database.Engine(DB_PATH)


#CONSTANTS DEFINING DIFFERENT USERS AND USER PROPERTIES
MESSAGE1_ID = 'msg-1'

MESSAGE1 = {'messageid': 'msg-1',
            'title': 'CSS: Margin problems with IE',
            'body': "I am using a float layout on my website but I've run \
into some problems with Internet Explorer. I have set the left margin of a \
float to 100 pixels, but IE uses a margin of 200px instead. Why is that? \
Is this one of the many bugs in IE?",
            'timestamp': 1362017481, 'replyto': None, 'sender': 'AxelW',
            'editor': None}

MESSAGE1_MODIFIED = {'messageid': MESSAGE1_ID,
                     'title': 'new title',
                     'body': 'new body',
                     'timestamp': 1362017481, 'replyto': None,
                     'sender': 'AxelW', 'editor': 'new editor'}

MESSAGE2_ID = 'msg-10'

MESSAGE2 = {'messageid': 'msg-10',
            'title': 'WinZip',
            'body': "WinZip, for example. There are plenty of other \
applications that are capable of decompressing ZIP files, but WinZip is \
probably the most popular one. You can also try to google for UltimateZip, \
PowerArchiver, 7-Zip, IZArc and WinRAR. Choose whichever program you like.",
            'timestamp': 1362017481,
            'replyto': 'msg-1',
            'sender': 'Koodari',
            'editor': None}

WRONG_MESSAGE_ID = 'msg-200'

INITIAL_SIZE = 20


class MessageDBAPITestCase(unittest.TestCase):
    '''
    Test cases for the Messages related methods.
    '''
    #INITIATION AND TEARDOWN METHODS
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
        #This method load the initial values from forum_data_dump.sql
        ENGINE.populate_tables()

        #Creates a Connection instance to use the API
        self.connection = ENGINE.connect()

    def tearDown(self):
        '''
        Close underlying connection and remove all records from database
        '''
        self.connection.close()
        ENGINE.clear()

    def test_messages_table_created(self):
        '''
        Checks that the table initially contains 20 messages (check
        forum_data_dump.sql). NOTE: Do not use Connection instance but
        call directly SQL.
        '''
        print '('+self.test_messages_table_created.__name__+')', \
                  self.test_messages_table_created.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            users = cur.fetchall()
            #Assert
            self.assertEquals(len(users), INITIAL_SIZE)

    def test_create_message_object(self):
        '''
        Check that the method _create_message_object works return adequate
        values for the first database row. NOTE: Do not use Connection instace
        to extract data from database but call directly SQL.
        '''
        print '('+self.test_create_message_object.__name__+')', \
              self.test_create_message_object.__doc__
        #Create the SQL Statement
        keys_on = 'PRAGMA foreign_keys = ON'
        query = 'SELECT * FROM messages WHERE message_id = 1'
        #Get the sqlite3 con from the Connection instance
        con = self.connection.con
        with con:
            #Cursor and row initialization
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            #Provide support for foreign keys
            cur.execute(keys_on)
            #Execute main SQL Statement
            cur.execute(query)
            #Extrac the row
            row = cur.fetchone()
        #Test the method
        message = self.connection._create_message_object(row)
        self.assertDictContainsSubset(message, MESSAGE1)

    def test_get_message(self):
        '''
        Test get_message with id msg-1 and msg-10
        '''
        print '('+self.test_get_message.__name__+')', \
              self.test_get_message.__doc__
        #Test with an existing message
        message = self.connection.get_message(MESSAGE1_ID)
        self.assertDictContainsSubset(message, MESSAGE1)
        message = self.connection.get_message(MESSAGE2_ID)
        self.assertDictContainsSubset(message, MESSAGE2)

    def test_get_message_malformedid(self):
        '''
        Test get_message with id 1 (malformed)
        '''
        print '('+self.test_get_message_malformedid.__name__+')', \
              self.test_get_message_malformedid.__doc__
        #Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.get_message('1')

    def test_get_message_noexistingid(self):
        '''
        Test get_message with msg-200 (no-existing)
        '''
        print '('+self.test_get_message_noexistingid.__name__+')',\
              self.test_get_message_noexistingid.__doc__
        #Test with an existing message
        message = self.connection.get_message(WRONG_MESSAGE_ID)
        self.assertIsNone(message)

    def test_get_messages(self):
        '''
        Test that get_messages work correctly
        '''
        print '('+self.test_get_messages.__name__+')', self.test_get_messages.__doc__
        messages = self.connection.get_messages()
        #Check that the size is correct
        self.assertEquals(len(messages), INITIAL_SIZE)
        #Iterate throug messages and check if the messages with MESSAGE1_ID and
        #MESSAGE2_ID are correct:
        for message in messages:
            if message['messageid'] == MESSAGE1_ID:
                self.assertEquals(len(message), 4)
                self.assertDictContainsSubset(message, MESSAGE1)
            elif message['messageid'] == MESSAGE2_ID:
                self.assertEquals(len(message), 4)
                self.assertDictContainsSubset(message, MESSAGE2)

    def test_get_messages_specific_user(self):
        '''
        Get all messages from user Mystery. Check that their ids are 13 and 14.
        '''
        #Messages sent from Mystery are 13 and 14
        print '('+self.test_get_messages_specific_user.__name__+')', \
              self.test_get_messages_specific_user.__doc__
        messages = self.connection.get_messages(nickname="Mystery")
        self.assertEquals(len(messages), 2)
        #Messages id are 13 and 14
        for message in messages:
            self.assertIn(message['messageid'], ('msg-13', 'msg-14'))
            self.assertNotIn(message['messageid'], ('msg-1', 'msg-2',
                                                    'msg-3', 'msg-4'))

    def test_get_messages_length(self):
        '''
        Check that the number_of_messages  is working in get_messages
        '''
        #Messages sent from Mystery are 2
        print '('+self.test_get_messages_length.__name__+')',\
              self.test_get_messages_length.__doc__
        messages = self.connection.get_messages(nickname="Mystery",
                                                number_of_messages=2)
        self.assertEquals(len(messages), 2)
        #Number of messages is 20
        messages = self.connection.get_messages(number_of_messages=1)
        self.assertEquals(len(messages), 1)

    def test_delete_message(self):
        '''
        Test that the message msg-1 is deleted
        '''
        print '('+self.test_delete_message.__name__+')', \
              self.test_delete_message.__doc__
        resp = self.connection.delete_message(MESSAGE1_ID)
        self.assertTrue(resp)
        #Check that the messages has been really deleted throug a get
        resp2 = self.connection.get_message(MESSAGE1_ID)
        self.assertIsNone(resp2)

    def test_delete_message_malformedid(self):
        '''
        Test that trying to delete message wit id ='2' raises an error
        '''
        print '('+self.test_delete_message_malformedid.__name__+')', \
              self.test_delete_message_malformedid.__doc__
        #Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.delete_message('1')

    def test_delete_message_noexistingid(self):
        '''
        Test delete_message with  msg-200 (no-existing)
        '''
        print '('+self.test_delete_message_noexistingid.__name__+')', \
              self.test_delete_message_noexistingid.__doc__
        #Test with an existing message
        resp = self.connection.delete_message(WRONG_MESSAGE_ID)
        self.assertFalse(resp)

    def test_modify_message(self):
        '''
        Test that the message msg-1 is modifed
        '''
        print '('+self.test_modify_message.__name__+')', \
              self.test_modify_message.__doc__
        resp = self.connection.modify_message(MESSAGE1_ID, "new title",
                                              "new body", "new editor")
        self.assertEquals(resp, MESSAGE1_ID)
        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(MESSAGE1_ID)
        self.assertDictContainsSubset(resp2, MESSAGE1_MODIFIED)

    def test_modify_message_malformedid(self):
        '''
        Test that trying to modify message wit id ='2' raises an error
        '''
        print '('+self.test_modify_message_malformedid.__name__+')',\
              self.test_modify_message_malformedid.__doc__
        #Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.modify_message('1', "new title", "new body",
                                           "editor")

    def test_modify_message_noexistingid(self):
        '''
        Test modify_message with  msg-200 (no-existing)
        '''
        print '('+self.test_modify_message_noexistingid.__name__+')',\
              self.test_modify_message_noexistingid.__doc__
        #Test with an existing message
        resp = self.connection.modify_message(WRONG_MESSAGE_ID, "new title",
                                              "new body", "editor")
        self.assertIsNone(resp)

    def test_create_message(self):
        '''
        Test that a new message can be created
        '''
        print '('+self.test_create_message.__name__+')',\
              self.test_create_message.__doc__
        messageid = self.connection.create_message("new title", "new body",
                                                   "Koodari")
        self.assertIsNotNone(messageid)
        #Get the expected modified message
        new_message = {}
        new_message['title'] = 'new title'
        new_message['body'] = 'new body'
        new_message['sender'] = 'Koodari'
        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(messageid)
        self.assertDictContainsSubset(new_message, resp2)
        #CHECK NOW NOT REGISTERED USER
        messageid = self.connection.create_message("new title", "new body",
                                                   "anonymous_User")
        self.assertIsNotNone(messageid)
        #Get the expected modified message
        new_message = {}
        new_message['title'] = 'new title'
        new_message['body'] = 'new body'
        new_message['sender'] = 'anonymous_User'
        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(messageid)
        self.assertDictContainsSubset(new_message, resp2)

    def test_append_answer(self):
        '''
        Test that a new message can be replied
        '''
        print '('+self.test_append_answer.__name__+')',\
              self.test_append_answer.__doc__
        messageid = self.connection.append_answer(MESSAGE1_ID,
                                            "new title", "new body", "Koodari")
        self.assertIsNotNone(messageid)
        #Get the expected modified message
        new_message = {}
        new_message['title'] = 'new title'
        new_message['body'] = 'new body'
        new_message['sender'] = 'Koodari'
        new_message['replyto'] = MESSAGE1_ID
        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(messageid)
        self.assertDictContainsSubset(new_message, resp2)
        #CHECK NOW NOT REGISTERED USER
        messageid = self.connection.append_answer(MESSAGE1_ID,
                                     "new title", "new body", "anonymous_User")
        self.assertIsNotNone(messageid)
        #Get the expected modified message
        new_message = {}
        new_message['title'] = 'new title'
        new_message['body'] = 'new body'
        new_message['sender'] = 'anonymous_User'
        new_message['replyto'] = MESSAGE1_ID
        #Check that the messages has been really modified through a get
        resp2 = self.connection.get_message(messageid)
        self.assertDictContainsSubset(new_message, resp2)

    def test_append_answer_malformed_id(self):
        '''
        Test that trying to reply message wit id ='2' raises an error
        '''
        print '('+self.test_append_answer_malformed_id.__name__+')',\
              self.test_append_answer_malformed_id.__doc__
        #Test with an existing message
        with self.assertRaises(ValueError):
            self.connection.append_answer('1', "new title", "new body",
                                          "Koodari")

    def test_append_answer_noexistingid(self):
        '''
        Test append_answer with  msg-200 (no-existing)
        '''
        print '('+self.test_append_answer_noexistingid.__name__+')',\
              self.test_append_answer_noexistingid.__doc__
        #Test with an existing message
        resp = self.connection.append_answer(WRONG_MESSAGE_ID,
                                "new title", "new body", "Koodari")
        self.assertIsNone(resp)

    def test_not_contains_message(self):
        '''
        Check if the database does not contain messages with id msg-200

        '''
        print '('+self.test_contains_message.__name__+')', \
              self.test_contains_message.__doc__
        self.assertFalse(self.connection.contains_message(WRONG_MESSAGE_ID))

    def test_contains_message(self):
        '''
        Check if the database contains messages with id msg-1 and msg-10

        '''
        print '('+self.test_contains_message.__name__+')', \
              self.test_contains_message.__doc__
        self.assertTrue(self.connection.contains_message(MESSAGE1_ID))
        self.assertTrue(self.connection.contains_message(MESSAGE2_ID))

if __name__ == '__main__':
    print 'Start running message tests'
    unittest.main()
