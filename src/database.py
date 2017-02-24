'''
Created on 13.02.2013

Modified on 18.02.2017

Provides the database API to access the forum persistent data.

@author: ivan, asare,arash, anastasiia

'''

import datetime
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
            cur.execute("DELETE FROM History")
            cur.execute("DELETE FROM Blood_Donors")
            cur.execute("DELETE FROM Blood_Banks")
            cur.execute("DELETE FROM Blood_Types")
            cur.execute("DELETE FROM Current_Blood_State")

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

        donorId = 'bdonor-' + str(row['donorId'])
        firstname = row['firstname']
        familyName = row['familyName']
        birthDate = row['birthDate'] if row['birthDate'] is not None else None
        gender = row['gender'] if row['gender'] is not None else None
        bloodTypeId ='btype-'+str(row['bloodTypeId']) if row[
            'bloodTypeId'] is not None else None
        telephone =str(row['telephone'])
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
        bloodTypeId = row['bloodTypeId'] if row[
            'bloodTypeId'] is not None else None
        bloodBankId = row['bloodBankId'] if row[
            'bloodBankId'] is not None else None
        amount = row['amount']
        timeStamp = row['timeStamp']

        history = {
            'historyId': historyId, 'donorId': donorId,
            'bloodTypeId': bloodTypeId, 'bloodBankId': bloodBankId,
            'amount': amount, 'timeStamp': timeStamp
        }

        return history

    def _create_current_blood_state_object(self, row):
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
        bloodTypeId = row['bloodTypeId'] if row[
            'bloodTypeId'] is not None else None
        bloodBankId = row['bloodBankId'] if row[
            'bloodBankId'] is not None else None
        amount = row['amount']
        timeStamp = row['timeStamp'] if row[
            'bloodBankId'] is not None else None

        bloodState = {
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
        # Extracts the int which is the id for a Blood bank in the database
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
        stmnt = 'DELETE FROM Blood_Banks WHERE bloodBankId = ?'
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

    def modify_blood_bank(self, bloodBankId, name=None, address=None, city=None, email=None, telephone=None, latitude=None, longitude=None, threshold=None):
        '''
        Modifies a Blood Bank based  ``bloodBankId`` and any of the Blood attributes
        :param str bloodBankId: The id of the Blood Bank to modify. Note that
            bloodBankId is a string with format bbank-\d{1,3}
        :param str name: the blood bank's name
        :param str city: the blood bank's city
        :param str telephone: the blood bank's telephone
        :param str address: the blood bank's address
        :param str email: the blood bank's email
        :param str threshold: the blood bank's threshold(int)
        :param str latitude: the blood bank's latitude (REAL or decimal)
        :param str longitude: the blood bank's longitude(int)

        :return: the id of the edited blood bank or None if the blood bank 
             column(s) to modify were not found. The id of the blood bank has the format ``bbank-\d{1,3}``,
              where \d{1,3} is the id of the blood bank in the database.
        :raises ValueError: if the bloodBankId has a wrong format.

         Note that the method can be used by passing the bloodBankId, and any other combination of parameters
        '''

        # Extracts the int which is the id for a Blood bank in the database
        match = re.match(r'bbank-(\d{1,3})', bloodBankId)
        if match is None:
            raise ValueError("The bloodBankId is malformed")
        bloodBankId = int(match.group(1))

        # Create the SQL statment
        basic = 'UPDATE Blood_Banks SET '
        stmnt = 'UPDATE Blood_Banks SET '
        stmnt = stmnt + " name=? , " if name is not None else stmnt
        stmnt = stmnt + " address=? , " if address is not None else stmnt
        stmnt = stmnt + " city=? , " if city is not None else stmnt
        stmnt = stmnt + " email=? , " if email is not None else stmnt
        stmnt = stmnt + " telephone=? , " if telephone is not None else stmnt
        stmnt = stmnt + " latitude=? , " if latitude is not None else stmnt
        stmnt = stmnt + " longitude=? , " if longitude is not None else stmnt
        stmnt = stmnt + " threshold=? , " if threshold is not None else stmnt

        if basic <> stmnt:
            stmnt = stmnt + " WHERE bloodBankId=?"
        else:
            return None
        # try removing the last comma before WWHERE clause in the query
        stmnt = ' '.join(stmnt.rsplit(',', 1))
        #replace_right(stmnt,',',' ',1)

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement

        pvalue = ()
        pvalue = pvalue + (name,) if name is not None else pvalue
        pvalue = pvalue + (address,) if address is not None else pvalue
        pvalue = pvalue + (city,) if city is not None else pvalue
        pvalue = pvalue + (email,) if email is not None else pvalue
        pvalue = pvalue + (telephone,) if telephone is not None else pvalue
        pvalue = pvalue + (latitude,) if latitude is not None else pvalue
        pvalue = pvalue + (longitude,) if longitude is not None else pvalue
        pvalue = pvalue + (threshold,) if threshold is not None else pvalue
        pvalue = pvalue + (bloodBankId,)

        cur.execute(stmnt, pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return None
        return 'bbank-' + str(bloodBankId)

    def create_blood_bank(self, name, city, telephone, email, threshold, address="-", latitude=None,
                          longitude=None):
        '''
        Create a new Blood Bank with the data provided as arguments.

        :param str name: the blood bank's name
        :param str city: the blood bank's city
        :param str telephone: the blood bank's telephone
        :param str email: the blood bank's email
        :param str threshold: the blood bank's content
        :param str address: the blood bank's address. can be None         
        :param str latitude: the blood bank's latitude ( REAL or decimal) . can be None              
        :param str longitude: the blood bank's longitude ( REAL or decimal)  . Can be None 


        :return: the id of the created Blood Bank or None if the Blood bank could not
            be created, Note that the returned value is a string with the format bbank-\d{1,3}.

        :raises sqlite3.DatabaseError: if the database could not be modified.
        :raises sqlite3.IntegrityError: if an entry with same name, email could not be modified.

        '''
        # Create the SQL statment
        query = 'INSERT INTO Blood_Banks(name,address,city,telephone,email,\
                    latitude,longitude,threshold) VALUES (?,?,?,?,?,?,?,?)'

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Execute SQL Statement to get userid given nickname
        pvalue = (name, address, city, telephone, email,
                  latitude, longitude, threshold,)
        cur.execute(query, pvalue)
        self.con.commit()
        # Extract the id of the added message
        lid = cur.lastrowid
        # Return the id in
        return 'bbank-' + str(lid) if lid is not None else None

    # Blood_Types API
    def get_blood_types(self):
        '''
        Return a list of all the Blood types in the database

        :return: A list of Blood_Types. or None of no Blood Types exists.
            Each entry is a dictionary containing the following keys:

            * ``bloodTypeId``: string with format btypeid-\d{1,3}. Id of Blood Typoe
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

    def get_blood_type(self, bloodTypeId):
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

    def create_blood_type(self, name):
        '''
        Create a new blood type.
        :param str name: the blood type's name
        :return: the id of the created Blood Type or None if the Blood type could not
            be created, Note that 
            the returned value is a string with the format btype-\d{1,3}.
        :raises DatabaseError: if the database could not be create.
        :raises IntegrityError: if Blood type with same name exists
        :raises ValueError: if the name is empty
        '''

        # Create the SQL statment
        if not name:
            raise ValueError("Name cannot be empty")

        stmnt = 'INSERT INTO Blood_Types (name) \
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
        # TODO update documenation ,

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

        pvalue = (name, bloodTypeId)

        cur.execute(stmnt, pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return None
        return 'btype-' + str(bloodTypeId)

    def delete_blood_type(self, bloodTypeId):
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

    # Blood_Donors Table API.
    def get_blood_donors(self):
        '''
        Return a list of all the Blood donors in the database

        :return: A list of Blood_Donors. or None of no Blood Donors exists.
            Each entry is a dictionary containing the following keys:

            * ``donorId``: string with format bdonor-\d{1,3}. Id of Blood Donor
            * ``firstname``: First name of the Blood Donor
            * ``familyName``:  FamilyName of the Blood Donor
            * ``birthDate``:  Date of birth of the Blood Donor
            * ``gender``:  Gender of te Blood Donor
            * ``bloodTypeId``:  The ID of the Blood type of the Blood Donor
            * ``telephone``:  Blood Donor's telephone
            * ``city``:  Blood Donor's city
            * ``address``: Blood Donor's address
            * ``email``: Blood Donor's e-mail

            Note that all values in the returned dictionary are string unless
            otherwise stated.

        '''
        # Create the SQL Statement

        query = 'SELECT * FROM Blood_Donors'

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
        bloodDonors = []
        for row in rows:
            donor = self._create_blood_donor_object(row)
            bloodDonors.append(donor)
        return bloodDonors

    def get_blood_donor(self, bloodDonorId):
        '''
        Extracts a blood donor record from the database.

        :param bloodDonorId: The id of the Blood Bank. Note that bloodDonorId is a
            string with format ``bdonor-\d{1,3}``.
        :return: A dictionary with the format provided in
            :py:meth:`_create_blood_donor_object` or None if the Blood Donor with provided 
            id does not exist.
        :raises ValueError: when ``bloodDonorId`` is not well formed

        '''
        # Extracts the int which is the id for a Blood bank in the database
        match = re.match(r'bdonor-(\d{1,3})', bloodDonorId)
        if match is None:
            raise ValueError("The bloodDonorId is malformed")
        bloodDonorId = int(match.group(1))

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Create the SQL Query
        query = 'SELECT * FROM Blood_Donors WHERE donorId = ?'
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement
        pvalue = (bloodDonorId,)
        cur.execute(query, pvalue)
        # Process the response.
        # Just one row is expected
        row = cur.fetchone()
        if row is None:
            return None
        # Build the return object
        return self._create_blood_donor_object(row)

    def create_blood_donor(self, firstname, familyName, telephone, email, bloodTypeId, birthDate, gender, address="-",city=None):
        '''
        Create a new Blood Donor with the data provided as arguments.

        :param str firstname: the Blood Donor's firstname
        :param str familyName: the blood donor's familyName
        :param str telephone: the blood donor's telephone
        :param str email: the blood donor's email
        :param str bloodTypeId: the blood donor's bloodTypeId in the form btype-\d{1,3}
        :param str birthDate: the blood donor's birthDate, in the format dd-mm-YYYY example 12-08-2015        
        :param str gender: the blood donor's gender, MALE or FEMALE         
        :param str address: the blood donor's address
        :param str address: the blood donor's city


        :return: the id of the created blood donor or None if the blood donor could not
            be created, Note that the returned value is a string with the format bdonor-\d{1,3}.

        :raises ValueError: if the bloodTypeId, birthDate, gender are in wrong formats
        :raises sqlite3.IntegrityError: if a blood donor same  email exists.

        '''
        ##print 'This si the blood type id'
        ##print  bloodTypeId
        # Extracts the int which is the id for a Blood Donor in the database
        match = re.match(r'btype-(\d{1,3})',str(bloodTypeId))
        if match is None:
            raise ValueError("The bloodTypeId is malformed")
        bloodTypeId = int(match.group(1))
       
        try:
            birthDate = datetime.datetime.strptime(birthDate, "%d-%m-%Y")
        except Exception as e:
            raise ValueError("The birthDate is not in the correct format")
        
        gender=gender.lower()
        
        if(gender != "MALE".lower() and gender!= "FEMALE".lower()):
            raise ValueError("The gender is not in the correct format")
        stmnt = 'INSERT INTO Blood_Donors \
                        (firstname,familyName,birthDate,gender,\
                            bloodTypeId,telephone,city,address,email) \
                 VALUES(?,?,?,?,?,?,?,?,?)'
        # Variables for the statement.

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()

        # Execute SQL Statement
        pvalue = (firstname, familyName, birthDate, gender,
                  bloodTypeId, telephone, city, address, email,)

        cur.execute(stmnt, pvalue)
        self.con.commit()
        # Extract the id of the added message
        lid = cur.lastrowid
        # Return the id in
        return 'bdonor-' + str(lid) if lid is not None else None

    def modify_blood_donor(self, bloodDonorId, firstname=None, familyName=None, telephone=None, 
                            email=None, bloodTypeId=None, birthDate=None, gender=None, 
                            address=None,city=None):
        '''
        Modifies a Blood Donor based  ``bloodDonorId`` and any of the Blood attributes


        :param str bloodDonorId: The id of the Blood Donor to modify. Note that
            bloodDonorId is a string with format bdonor-\d{1,3}
        :param str firstname: the Blood Donor's firstname
        :param str familyName: the blood donor's familyName
        :param str telephone: the blood donor's telephone
        :param str email: the blood donor's email
        :param str bloodTypeId: the blood donor's bloodTypeId in the form btype-\d{1,3}
        :param str birthDate: the blood donor's birthDate, in the format dd-mm-YYYY example 12-08-2015        
        :param str gender: the blood donor's gender, MALE or FEMALE         
        :param str address: the blood donor's address
        :param str city: the blood donor's city

        :return: the id of the edited Blood Donor or None if the Blood Donor
             column(s) to modify were not found. The id of the Blood Donor has the format ``bdonor-\d{1,3}``,
              where \d{1,3} is the id of the Blood Donor in the database.

        :raises ValueError: if the bloodDonorId, bloodTypeId, birthDate, gender are in wrong formats
        :raises sqlite3.IntegrityError: if bloodTypeId references a non existent blood type

         Note that the method can be used by passing the bloodDonorId, and any other combination of parameters
        '''

        match = re.match(r'bdonor-(\d{1,3})', str( bloodDonorId))
        if match is None:
            raise ValueError("The bloodDonorId is malformed")
        bloodDonorId = int(match.group(1))

        if bloodTypeId:

            match2 = re.match(r'btype-(\d{1,3})',str( bloodTypeId))
            if match2 is None:
                raise ValueError("The bloodTypeId is malformed")
            bloodTypeId = int(match2.group(1))
        
        if birthDate:
            try:
                birthDate = datetime.strftime(birthDate, "%d-%m-%y")
            except Exception as e:
                raise ValueError("The birthDate is not in the correct format")
        if gender:

            gender=gender.lower()
            if(gender != 'MALE'.lower() or gender!= 'FEMALE'.lower()):
                raise ValueError("The gender is not in the correct format")

        # Create the SQL statment
        basic = 'UPDATE Blood_Donors SET '
        stmnt = 'UPDATE Blood_Donors SET '
        stmnt = stmnt + " firstname=? , " if firstname is not None else stmnt
        stmnt = stmnt + " familyName=? , " if familyName is not None else stmnt
        stmnt = stmnt + " birthDate=? , " if birthDate is not None else stmnt
        stmnt = stmnt + " gender=? , " if gender is not None else stmnt
        stmnt = stmnt + " bloodTypeId=? , " if bloodTypeId is not None else stmnt
        stmnt = stmnt + " telephone=? , " if telephone is not None else stmnt
        stmnt = stmnt + " city=? , " if city is not None else stmnt
        stmnt = stmnt + " address=? , " if address is not None else stmnt
        stmnt = stmnt + " email=? , " if email is not None else stmnt
        stmnt = stmnt + " city=? , " if city is not None else stmnt

        if basic <> stmnt:
            stmnt = stmnt + " WHERE donorId=?"
        else:
            return None
        # try removing the last comma before WWHERE clause in the query
        stmnt = ' '.join(stmnt.rsplit(',', 1))
        #replace_right(stmnt,',',' ',1)

        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        # Execute main SQL Statement

        pvalue = ()
        pvalue = pvalue + (firstname,) if firstname is not None else pvalue
        pvalue = pvalue + (familyName,) if familyName is not None else pvalue
        pvalue = pvalue + (birthDate,) if birthDate is not None else pvalue
        pvalue = pvalue + (gender,) if gender is not None else pvalue
        pvalue = pvalue + (bloodTypeId,) if bloodTypeId is not None else pvalue
        pvalue = pvalue + (telephone,) if telephone is not None else pvalue
        pvalue = pvalue + (city,) if city is not None else pvalue
        pvalue = pvalue + (address,) if address is not None else pvalue
        pvalue = pvalue + (email,) if email is not None else pvalue
        pvalue = pvalue + (city,) if city is not None else pvalue
        pvalue = pvalue + (bloodDonorId,)

        cur.execute(stmnt, pvalue)
        self.con.commit()
        if cur.rowcount < 1:
            return None
        return 'bdonor-' + str(bloodDonorId)
    def delete_blood_donor(self, bloodDonorId):
        '''
        Delete the Blood Donor with id given as parameter.
        :param str bloodDonorId: id of the Blood Donor to remove.Note that bloodDonorId
            is a string with format ``bdonor-\d{1,3}``
        :return: True if the Blood Donor has been deleted, False otherwise
        :raises ValueError: if the bloodDonorId has a wrong format.

        '''
        # Extracts the int which is the id for a message in the database

        match = re.match(r'bdonor-(\d{1,3})', bloodDonorId)
        if match is None:
            raise ValueError("The bloodDonorId is malformed")
        bloodDonorId = int(match.group(1))

        # Create the SQL statment
        stmnt = 'DELETE FROM Blood_Donors WHERE donorId = ?'
        # Activate foreign key support
        self.set_foreign_keys_support()
        # Cursor and row initialization
        self.con.row_factory = sqlite3.Row
        cur = self.con.cursor()
        pvalue = (bloodDonorId,)
        cur.execute(stmnt, pvalue)
        # Commit the message
        self.con.commit()
        # Check that the message has been deleted
        if cur.rowcount < 1:
            return False
        # Return true if message is deleted.
        return True
