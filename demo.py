'''
Created on 02.03.2017

Run some database API methods

@author: asare

'''
import sqlite3
import pprint

from src import database

DB_PATH = 'db/bloodAlert.db'
ENGINE = database.Engine(DB_PATH)



api=ENGINE.connect()

#blood blank demoa

print '\nAll blood banks \n\t'
banks=api.get_blood_banks()

pprint.pprint (banks)

print '\nAll blood banks \n\t'
pprint.pprint(api.get_blood_bank('bbank-2'))

print '\n trying  \n\t'
pprint.pprint(api.create_blood_type("O+"))
pprint.pprint(api.get_blood_types())


#echo api.get_blood_bank('bbank-2') | python -mjson.tool

