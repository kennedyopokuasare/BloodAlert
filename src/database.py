'''
Created on 13.02.2013

Modified on 18.02.2017

Provides the database API to access the forum persistent data.

@author: ivan, asare,arash, anastasiia

'''

from datetime import datetime
import time
import sqlite3
import re
import os

# Default paths for .db and .sql files to create and populate the database.
DEFAULT_DB_PATH = 'db/bloodAlert.db'
DEFAULT_SCHEMA = "db/bloodAlert_schema_dump.sql"
DEFAULT_DATA_DUMP = "db/bloodAlert_data_dump.sql"


class Engine(object):
    '''
    Abstraction of the database.

    It includes tools to create, configure,
    populate and connect to the sqlite file. You can access the Connection
    instance, and hence, to the database interface itself using the method
    :py:meth:`connection`.

    :Example:

    >>> engine = Engine()
    >>> con = engine.connect()

    :param db_path: The path of the database file (always with respect to the
        calling script. If not specified, the Engine will use the file located
        at *db/forum.db*

    '''

    def __init__(self, db_path=None):
        '''
        '''

        super(Engine, self).__init__()
        if db_path is not None:
            self.db_path = db_path
        else:
            self.db_path = DEFAULT_DB_PATH

    def connect(self):
        '''
        Creates a connection to the database.

        :return: A Connection instance
        :rtype: Connection

        '''
        return Connection(self.db_path)

    def remove_database(self):
        '''
        Removes the database file from the filesystem.

        '''
        if os.path.exists(self.db_path):
            # THIS REMOVES THE DATABASE STRUCTURE
            os.remove(self.db_path)

    def clear(self):
        '''
        Purge the database removing all records from the tables. However,
        it keeps the database schema (meaning the table structure)

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        # THIS KEEPS THE SCHEMA AND REMOVE VALUES
        con = sqlite3.connect(self.db_path)
        # Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        with con:
            cur = con.cursor()
            cur.execute("DELETE FROM Blood_Donors")
            cur.execute("DELETE FROM Blood_Banks")
            cur.execute("DELETE FROM Blood_Types")
            cur.execute("DELETE FROM Current_Blood_State")
            # NOTE since we have ON DELETE CASCADE  IN History
            # , WE DO NOT HAVE TO WORRY TO CLEAR THAT TABLE.

    # METHODS TO CREATE AND POPULATE A DATABASE USING DIFFERENT SCRIPTS
    def create_tables(self, schema=None):
        '''
        Create programmatically the tables from a schema file.

        :param schema: path to the .sql schema file. If this parmeter is
            None, then "db/bloodAlert_schema_dump.sql" is utilized.

        '''
        con = sqlite3.connect(self.db_path)
        if schema is None:
            schema = DEFAULT_SCHEMA
        try:
            with open(schema) as f:
                sql = f.read()
                cur = con.cursor()
                cur.executescript(sql)
        finally:
            con.close()

    def populate_tables(self, dump=None):
        '''
        Populate programmatically the tables from a dump file.

        :param dump:  path to the .sql dump file. If this parmeter is
            None, then "db/bloodAlert_data_dump.sql" is utilized.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        con = sqlite3.connect(self.db_path)
        # Activate foreing keys support
        cur = con.cursor()
        cur.execute(keys_on)
        # Populate database from dump
        if dump is None:
            dump = DEFAULT_DATA_DUMP
        with open(dump) as f:
            sql = f.read()
            cur = con.cursor()
            cur.executescript(sql)

    # METHODS TO CREATE THE TABLES PROGRAMMATICALLY WITHOUT USING SQL SCRIPT
    def create_blood_type_table(self):
        '''
        Create the table ``Blood_Type`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Blood_Types( bloodTypeId INTEGER PRIMARY KEY AUTOINCREMENT,\
                    name TEXT NOT NULL UNIQUE)'
                
        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_blood_banks_table(self):
        '''
        Create the table ``Blood_Banks`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''

        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE  Blood_Banks(\
                    bloodBankId INTEGER PRIMARY KEY AUTOINCREMENT,\
                    name TEXT NOT NULL UNIQUE,   address TEXT, \
                    city TEXT NOT NULL,  telephone TEXT NOT NULL,\
                    email TEXT NOT NULL, latitude REAL,\
                    longitude REAL, threshold INTEGER NOT NULL )'

        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_blood_donors_table(self):
        '''
        Create the table ``Blood_Donors`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE Blood_Donors (\
                    donorId  INTEGER PRIMARY KEY AUTOINCREMENT,\
                    firstname TEXT NOT NULL,\
                    familyName TEXT NOT NULL,\
                    birthDate TEXT,\
                    gender  TEXT,\
                    bloodTypeId INTEGER,\
                    telephone TEXT NOT NULL,\
                    city TEXT,\
                    address TEXT,\
                    email TEXT NOT NULL,\
                    FOREIGN KEY(bloodTypeId) REFERENCES BloodTypes(bloodTypeId) ON DELETE SET NULL)'

        # Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_history_table(self):
        '''
        Create the table ``History`` programmatically, without using
        .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'

        stmnt = 'CREATE TABLE  History(\
                    historyId INTEGER PRIMARY KEY AUTOINCREMENT,\
                    donorId  INTEGER NOT NULL,\
                    bloodTypeId INTEGER,  \
                    bloodBankId INTEGER, amount INTEGER NOT NULL,\
                    timeStamp REAL NOT NULL, \
                    FOREIGN KEY(donorId) REFERENCES Blood_Donors(donorId) ON DELETE CASCADE,\
                    FOREIGN KEY(bloodTypeId) REFERENCES BloodTypes(bloodTypeId) ON DELETE SET NULL,\
                    FOREIGN KEY(bloodBankId) REFERENCES Blood_Banks(bloodBankId) ON DELETE SET NULL)'

        # Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
                return False
        return True

    def create_current_blood_state_table(self):
        '''
        Create the table ``current_blood_state`` programmatically, without using .sql file.

        Print an error message in the console if it could not be created.

        :return: ``True`` if the table was successfully created or ``False``
            otherwise.
        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        stmnt = 'CREATE TABLE IF NOT EXISTS Current_Blood_State(\
                    bloodStateId INTEGER PRIMARY KEY AUTOINCREMENT,\
                    bloodBankId INTEGER,\
                    bloodTypeId INTEGER,\
                    amount INTEGER ,\
                    timeStamp REAL,\
                    FOREIGN KEY(bloodBankId) REFERENCES Blood_Banks(bloodBankId) ON DELETE SET NULL,\
                    FOREIGN KEY(bloodTypeId) REFERENCES BloodType(bloodTypeId) ON DELETE SET NULL\
                    )'

        # Connects to the database. Gets a connection object
        con = sqlite3.connect(self.db_path)
        with con:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = con.cursor()
            try:
                cur.execute(keys_on)
                # execute the statement
                cur.execute(stmnt)
            except sqlite3.Error, excp:
                print "Error %s:" % excp.args[0]
        return None


class Connection(object):
    '''
    API to access the BloodAlert database.

    The sqlite3 connection instance is accessible to all the methods of this
    class through the :py:attr:`self.con` attribute.

    An instance of this class should not be instantiated directly using the
    constructor. Instead use the :py:meth:`Engine.connect`.

    Use the method :py:meth:`close` in order to close a connection.
    A :py:class:`Connection` **MUST** always be closed once when it is not going to be
    utilized anymore in order to release internal locks.

    :param db_path: Location of the database file.
    :type dbpath: str

    '''

    def __init__(self, db_path):
        super(Connection, self).__init__()
        self.con = sqlite3.connect(db_path)

    def close(self):
        '''
        Closes the database connection, commiting all changes.

        '''
        if self.con:
            self.con.commit()
            self.con.close()

    # FOREIGN KEY STATUS
    def check_foreign_keys_status(self):
        '''
        Check if the foreign keys has been activated.

        :return: ``True`` if  foreign_keys is activated and ``False`` otherwise.
        :raises sqlite3.Error: when a sqlite3 error happen. In this case the
            connection is closed.

        '''
        try:
            # Create a cursor to receive the database values
            cur = self.con.cursor()
            # Execute the pragma command
            cur.execute('PRAGMA foreign_keys')
            # We know we retrieve just one record: use fetchone()
            data = cur.fetchone()
            is_activated = data == (1,)
            print "Foreign Keys status: %s" % 'ON' if is_activated else 'OFF'
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            self.close()
            raise excp
        return is_activated

    def set_foreign_keys_support(self):
        '''
        Activate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = ON'
        try:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, ON
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    def unset_foreign_keys_support(self):

        '''
        Deactivate the support for foreign keys.

        :return: ``True`` if operation succeed and ``False`` otherwise.

        '''
        keys_on = 'PRAGMA foreign_keys = OFF'
        try:
            # Get the cursor object.
            # It allows to execute SQL code and traverse the result set
            cur = self.con.cursor()
            # execute the pragma command, OFF
            cur.execute(keys_on)
            return True
        except sqlite3.Error, excp:
            print "Error %s:" % excp.args[0]
            return False

    
    
    
    # HELPERS
    # Here the helpers that transform database rows into dictionary. They work
    # similarly to ORM


    def _create_blood_type_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary 
        of  a Blood Type record.
        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``bloodTypeId``: id of the Blood Type (int)
            * ``name``: Blood Type's name

            Note that all values in the returned dictionary are string unless
            otherwise stated.
        '''
        bloodTypeId = 'btype-' + str(row['bloodTypeId'])
        name = row['name']
        bloodType = {
            'bloodTypeId': bloodTypeId, 'name': name,
        }
        return bloodType

    def _create_blood_bank_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary 
        of a Blood Bank record.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``bloodBankId``: id of the Blood Bank (int)
            * ``name``: Blood bank's name
            * ``address``:  Blood bank's address
            * ``city``:  Blood bank's city
            * ``telephone``:  Blood bank's telephone
            * ``email``:  Blood bank's email
            * ``latitude``:  Blood bank's latitude (long integer)
            * ``longitude``:  Blood bank's longitude (long integer)
            * ``threshold``: Blood bank's minimun threshold to call for blood (int)

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        bloodBankId = 'bbank-' + str(row['bloodBankId'])
        name = row['name']
        address = row['address'] if row['address'] is not None else None
        city = row['city']
        telephone = row['telephone']
        email = row['email']
        latitude = row['latitude'] if row['latitude'] is not None else None
        longitude = row['longitude'] if row['longitude'] is not None else None
        threshold = row['threshold']

        bloodBank = {
            'bloodBankId': bloodBankId, 'name': name,
            'address': address, 'city': city,
            'telephone': telephone, 'email': email,
            'latitude': latitude, 'longitude': longitude,
            'threshold': threshold
        }
        return bloodBank

    def _create_blood_donor_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary 
        of a Blood Donor record.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``donorId``: id of the Blood donor (int)
            * ``firstname``: Blood donor's firstname
            * ``familyName``:  Blood donor's family name or surname
            * ``birthDate``:  Blood donors's date of birth
            * ``telephone``:  Blood donor's telephone
            * ``gender``:  Blood donor's gender
            * ``bloodTypeId``:  Blood donor's bloodTypeId (int)
            * ``city``:  Blood donor's city
            * ``address``: Blood donor's address
            * ``email``: Blood donor's email

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''

        donorId ='bdonor-' + str(row['donorId'])
        firstname = row['firstname']
        familyName = row['familyName']
        birthDate = row['birthDate'] if row['birthDate'] is not None else None
        gender = row['gender'] if row['gender'] is not None else None
        bloodTypeId = row['bloodTypeId'] if row[
            'bloodTypeId'] is not None else None
        telephone = row['telephone']
        city = row['city'] if row['city'] is not None else None
        address = row['address'] if row['address'] is not None else None
        email = row['email']

        blood_donor = {
            'donorId': donorId, 'firstname': firstname, 'familyName': familyName,
            'birthDate': birthDate, 'gender': gender, 'bloodTypeId': bloodTypeId,
            'telephone': telephone, 'city': city, 'address': address,
            'email': email
        }

        return blood_donor

    def _create_history_object(self, row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary
        of a History record.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``historyId``: id of the Blood donation History (int)
            * ``donorId``: id of Blood donor (int)
            * ``bloodTypeId``: id of Blood Type donated (int)
            * ``bloodBankId``:  id of the blood bank where donation was made (int)
            * ``amount``:  amount of Blood donated (int)
            * ``timeStamp``: UNIX timestamp when the donated happened(long integer)

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        historyId = 'bdonor-' + str(row['historyId'])
        donorId = row['donorId']
        bloodTypeId = row['bloodTypeId'] if row['bloodTypeId'] is not None else None
        bloodBankId = row['bloodBankId'] if row['bloodBankId'] is not None else None
        amount = row['amount']
        timeStamp = row['timeStamp']

        history = {
            'historyId': historyId, 'donorId': donorId,
            'bloodTypeId': bloodTypeId, 'bloodBankId': bloodBankId,
            'amount': amount, 'timeStamp': timeStamp
        }

        return history

    def _create_current_blood_state_object(self,row):
        '''
        It takes a :py:class:`sqlite3.Row` and transform it into a dictionary
        of a Blood Bank's Current Blood State record.

        :param row: The row obtained from the database.
        :type row: sqlite3.Row
        :return: a dictionary containing the following keys:

            * ``bloodStateId``: id of the blood state entry (int)
            * ``bloodBankId``: id of Blood Bank associated with this entry (int)
            * ``bloodTypeId``: id of Blood Type (int)
            * ``amount``:  amount of Blood in current state (int)
            * ``timeStamp``: UNIX timestamp of the current blood state (long integer)

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        bloodStateId = 'bstate-' + str(row['bloodStateId'])
        bloodTypeId = row['bloodTypeId'] if row['bloodTypeId'] is not None else None
        bloodBankId = row['bloodBankId'] if row['bloodBankId'] is not None else None
        amount = row['amount']
        timeStamp = row['timeStamp'] if row['bloodBankId'] is not None else None

        bloodState={
            'bloodStateId': bloodStateId,
            'bloodTypeId': bloodTypeId, 'bloodBankId': bloodBankId,
            'amount': amount, 'timeStamp': timeStamp
        }
    
        return bloodState
   
    
    
    


   
   
    # API ITSELF
    # Blood_Banks Table API.

    def get_blood_banks(self):
        '''
        Return a list of all the Blood Banks in the database

        :return: A list of Blood_Banks. or None of no Blood Blanks exists.
            Each entry is a dictionary containing the following keys:

            * ``bloodBankId``: string with format bbankid-\d{1,3}. Id of Blood Bank
            * ``name``: Blood bank's name
            * ``address``:  Blood bank's address
            * ``city``:  Blood bank's city
            * ``telephone``:  Blood bank's telephone
            * ``email``:  Blood bank's email
            * ``latitude``:  Blood bank's latitude (long integer)
            * ``longitude``:  Blood bank's longitude (long integer)
            * ``threshold``: Blood bank's minimun threshold to call for blood (int)

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        # Create the SQL Statement 
        
        query = 'SELECT * FROM Blood_Banks'
        
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        cur.execute(query)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Build the return object
        bloodBanks = []
        for row in rows:
            bloodBank = self._create_blood_bank_object(row)
            bloodBanks.append(bloodBank)
        return bloodBanks
    def get_blood_bank(self, bloodBankId):
        '''
        Extracts a blood bank record from the database.

        :param bloodBankId: The id of the Blood Bank. Note that bloodBankId is a
            string with format ``bbank-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_blood_bank_object` or None if the Blood Bank with provided 
            id does not exist.
        :raises ValueError: when ``bloodBankId`` is not well formed

        '''
        # Extracts the int which is the id for a message in the database
        match = re.match(r'bbank-(\d{1,3})', bloodBankId)
        if match is None:
            raise ValueError("The bloodBankId is malformed")
        bloodBankId = int(match.group(1))

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Create the SQL Query
        query = 'SELECT * FROM Blood_Banks WHERE bloodBankId = ?'
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        pvalue = (bloodBankId,)
        cur.execute(query, pvalue)
        # Process the response.
        # Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        # Build the return object
        return self._create_blood_bank_object(row)

   

    def delete_blood_bank(self, bloodBankId):
        '''
        Delete the Blood Bank with id given as parameter.

        :param str bloodBankId: id of the Blood Bank to remove.Note that bloodBankId
            is a string with format ``bbank-\d{1,3}``
        :return: True if the Blood Bank has been deleted, False otherwise
        :raises ValueError: if the bloodBankId has a wrong format.

        '''
        # Extracts the int which is the id for a message in the database
        match = re.match(r'bbank-(\d{1,3})', bloodBankId)
        if match is None:
            raise ValueError("The bloodBankId is malformed")
        bloodBankId = int(match.group(1))
        
        # Create the SQL statment
        stmnt = 'DELETE FROM Blood:Banks WHERE bloodBankId = ?'
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (bloodBankId,)
        cur.execute(stmnt, pvalue)
        # Commit the message
        self.con.commit()
        # Check that the message has been deleted
        if cur.rowcount < 1:
            return False
        # Return true if message is deleted.
        return True

    def modify_blood_bank(self, bloodBankId, name=None, address=None,city=None, email=None,telephone=None, latitude=None, longitude=None,threshold=None):
        '''
        Modifies a Blood Bank based  ``bloodBankId`` on any of the Blood attributes
     

        :param str bloodBankId: The id of the Blood Bank to remove. Note that
            bloodBankId is a string with format bbank-\d{1,3}
        :param str title: the message's title
        :param str body: the message's content
       
        :return: the id of the edited message or None if the message was
              not found. The id of the message has the format ``msg-\d{1,3}``,
              where \d{1,3} is the id of the message in the database.
        :raises ValueError: if the messageid has a wrong format.

        '''
        #TODO update documenation , 

        # Extracts the int which is the id for a message in the database
        match = re.match(r'bbank-(\d{1,3})', bloodBankId)
        if match is None:
            raise ValueError("The messageid is malformed")
        messageid = int(match.group(1))
      
        # Create the SQL statment
        basic= 'UPDATE Blood_Banks SET '
        stmnt = 'UPDATE Blood_Banks SET '
        stmnt=stmnt+ " name=? , " if name is not None else stmnt
        stmnt=stmnt+ " address=? , " if address is not None else stmnt
        stmnt=stmnt+ " city=? , " if city is not None else stmnt
        stmnt=stmnt+ " email=? , " if email is not None else stmnt
        stmnt=stmnt+ " telephone=? , " if telephone is not None else stmnt
        stmnt=stmnt+ " latitude=? , " if latitude is not None else stmnt
        stmnt=stmnt+ " longitude=? , " if longitude is not None else stmnt
        stmnt=stmnt+ " threshold=? , " if threshold is not None else stmnt

        if basic<>stmnt:
            stmnt=stmnt+" WHERE bloodBankId=?"
        else:
            return None

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement

        pvalue=()
        pvalue = pvalue+(name,) if name is not None else pvalue
        pvalue = pvalue+(address,) if address is not None else pvalue
        pvalue = pvalue+(city,) if city is not None else pvalue
        pvalue = pvalue+(email,) if email is not None else pvalue
        pvalue = pvalue+(telephone,) if telephone is not None else pvalue
        pvalue = pvalue+(latitude,) if latitude is not None else pvalue
        pvalue = pvalue+(longitude,) if longitude is not None else pvalue
        pvalue = pvalue+(threshold,) if threshold is not None else pvalue
        pvalue+pvalue+(bloodBankId,)
        
        cur.execute(stmnt, pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return None
        return 'bbank-' + str(bloodBankId)

    def create_blood_bank(self, name,city, telephone,email,threshold, address="-",latitude=None,
                       longitude=None):
        '''
        Create a new BB with the data provided as arguments.

        :param str name: the message's title
        :param str city: the message's title
        :param str telephone: the message's title
        :param str email: the message's title
        :param str threshold: the message's content
        :param str address: the nickname of the person who is editing this
            message. If it is not provided "-" will be stored in db.
        :param str latitude: The ip address from which the message was created.
            It is a string with format "xxx.xxx.xxx.xxx". If no ipaddress is
            provided then database will store "0.0.0.0"
        :param str longitude: Only provided if this message is an answer to a
            previous message (parent). Otherwise, Null will be stored in the
            database. The id of the message has the format msg-\d{1,3}

        :return: the id of the created Blood Bank or None if the Blood bank could not
            be created, Note that 
            the returned value is a string with the format bbank-\d{1,3}.

        :raises ForumDatabaseError: if the database could not be modified.
        :raises ValueError: if the replyto has a wrong format.

        '''
        # Extracts the int which is the id for a message in the database
        if replyto is not None:
            match = re.match('msg-(\d{1,3})', replyto)
            if match is None:
                raise ValueError("The replyto is malformed")
            replyto = int(match.group(1))
       
        # Create the SQL statment
        # SQL to test that the message which I am answering does exist
        query1 = 'SELECT * from messages WHERE message_id = ?'
        # SQL Statement for getting the user id given a nickname
        query2 = 'SELECT user_id from users WHERE nickname = ?'
        # SQL Statement for inserting the data
        stmnt = 'INSERT INTO messages (title,body,timestamp,ip, \
                 timesviewed,reply_to,user_nickname,user_id) \
                 VALUES(?,?,?,?,?,?,?,?)'
        # Variables for the statement.
        # user_id is obtained from first statement.
        user_id = None
        timestamp = time.mktime(datetime.now().timetuple())
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # If exists the replyto argument, check that the message exists in
        # the database table
        if replyto is not None:
            pvalue = (replyto,)
            cur.execute(query1, pvalue)
            messages = cur.fetchall()
            if len(messages) < 1:
                return None
        # Execute SQL Statement to get userid given nickname
        pvalue = (sender,)
        cur.execute(query2, pvalue)
        # Extract user id
        row = cur.fetchone()
        if row is not None:
            user_id = row["user_id"]
        # Generate the values for SQL statement
        pvalue = (title, body, timestamp, ipaddress, 0, replyto, sender,
                  user_id)
        # Execute the statement
        cur.execute(stmnt, pvalue)
        self.con.commit()
        # Extract the id of the added message
        lid = cur.lastrowid
        # Return the id in
        return 'msg-' + str(lid) if lid is not None else None

    
  

    def contains_user(self, nickname):
        '''
        :return: True if the user is in the database. False otherwise
        '''
        return self.get_user_id(nickname) is not None
    
    
    
    
    
    
    # Blood Types API
    def get_blood_types(self):
        '''
        Return a list of all the Blood types in the database

        :return: A list of Blood_Types. or None of no Blood Types exists.
            Each entry is a dictionary containing the following keys:

            * ``bloodTypeId``: string with format btypeid-\d{1,3}. Id of Blood Tyoe
            * ``name``: Blood Type's name

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        # Create the SQL Statement 
        
        query = 'SELECT * FROM Blood_Types'
        
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        cur.execute(query)
        # Get results
        rows = cur.fetchall()
        if rows is None:
            return None
        # Build the return object
        bloodTypes = []
        for row in rows:
            bloodType = self._create_blood_type_object(row)
            bloodTypes.append(bloodType)
        return bloodTypes
       
    def get_blood_type(self,bloodTypeId):
        '''
        Extracts a blood type record from the database.

        :param bloodTypeId: The id of the Blood Type. Note that bloodTypeId is a
            string with format ``btype-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_blood_type_object` or None if the Blood Type with provided 
            id does not exist.
        :raises ValueError: when ``bloodTypeId`` is not well formed

        '''
        # Extracts the int which is the id for a message in the database
        match = re.match(r'btype-(\d{1,3})', bloodTypeId)
        if match is None:
            raise ValueError("The bloodTypeId is malformed")
        bloodTypeId = int(match.group(1))

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Create the SQL Query
        query = 'SELECT * FROM Blood_Types WHERE bloodTypeId = ?'
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        pvalue = (bloodTypeId,)
        cur.execute(query, pvalue)
        # Process the response.
        # Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        # Build the return object
        return self._create_blood_type_object(row)

    def create_blood_type(self,name):
        '''
        Create a new blood type.
        :param str name: the blood type's name
        :return: the id of the created Blood Type or None if the Blood type could not
            be created, Note that 
            the returned value is a string with the format btype-\d{1,3}.
        :raises DatabaseError: if the database could not create or some Blood Type with same name exists.
        :raises ValueError: if the replyto has a wrong format.
        '''
        
        # Create the SQL statment
      
       
        stmnt = 'INSERT INTO Blood_Type (name) \
                 VALUES(?)'
        # Variables for the statement.
      
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
       
        # Execute SQL Statement
        pvalue = (name,)
       
        cur.execute(stmnt, pvalue)
        self.con.commit()
        # Extract the id of the added message
        lid = cur.lastrowid
        # Return the id in
        return 'btype-' + str(lid) if lid is not None else None


    def modify_blood_type(self, bloodTypeId, name=None):
        '''
        Modifies a Blood type based  ``bloodTypeId`` on any of the Blood attributes
     

        :param str bloodTypeId: The id of the Blood Bank to remove. Note that
            bloodBankId is a string with format btype-\d{1,3}
        :param str name: the blood type's name
       
        :return: the id of the edited blood stype or None if the blood type was
              not found. The id of the blood type has the format ``btype-\d{1,3}``,
              where \d{1,3} is the id of the blood type in the database.
        :raises ValueError: if the bloodTypeId has a wrong format.

        '''
        #TODO update documenation , 

        # Extracts the int which is the id for a blood type in the database
        match = re.match(r'btype-(\d{1,3})', bloodTypeId)
        if match is None:
            raise ValueError("The blood type is malformed")
        bloodTypeId = int(match.group(1))
      
        # Create the SQL statment
       
        stmnt = 'UPDATE Blood_Types SET name=? WHERE bloodTypeId=?'

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement

        pvalue=(name,bloodTypeId)
      
        
        cur.execute(stmnt, pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return None
        return 'btype-' + str(bloodTypeId)


    def delete_blood_type(self,bloodTypeId): 
        '''
        Delete the Blood type with id given as parameter.

        :param str bloodTypeId: id of the Blood Type to remove. Note that bloodTypeId
            is a string with format ``btype-\d{1,3}``
        :return: True if the Blood Type has been deleted, False otherwise
        :raises ValueError: if the bloodTypeId has a wrong format.

        '''
        # Extracts the int which is the id for a message in the database
        match = re.match(r'btype-(\d{1,3})', bloodTypeId)
        if match is None:
            raise ValueError("The bloodTypeId is malformed")
        bloodTypeId = int(match.group(1))
        
        # Create the SQL statment
        stmnt = 'DELETE FROM Blood_Types WHERE bloodTypeId = ?'
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (bloodTypeId,)
        cur.execute(stmnt, pvalue)
        # Commit the message
        self.con.commit()
        # Check that the message has been deleted
        if cur.rowcount < 1:
            return False
        # Return true if message is deleted.
        return True