'''
Created on 21.02.2017

Creates and populated the BloodAlert database

@author: asare

'''
import sqlite3

from src import database

DB_PATH = 'db/bloodAlert.db'
ENGINE = database.Engine(DB_PATH)

print '\tRemoving old database if any'
ENGINE.remove_database()

print '\tCreating database'
ENGINE.create_tables()

print '\tpopulating database'
ENGINE.populate_tables()

