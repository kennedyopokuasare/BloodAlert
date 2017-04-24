"""
Created on 24.03.2016
@author: asare
@author: anastasiia
@author: arash
"""

import json

from flask import Flask, request, Response, g, _request_ctx_stack, redirect, send_from_directory
from flask_restful import Resource, Api, abort
from werkzeug.exceptions import HTTPException, NotFound


from utils import RegexConverter
import database


# The following codes was imported from PWP exercise and heavily modified to suite our work


#Constants for hypermedia formats and profiles
MASON = "application/vnd.mason+json"
JSON = "application/json"

BLOODALERT_BLOOD_BANK_PROFILE = "/profiles/blood-bank-profile/"
BLOODALERT_BLOOD_DONOR_PROFILE = "/profiles/blood-donor-profile/"
BLOODALERT_BLOOD_TYPES_PROFILE = "/profiles/blood-types-profile/"

ERROR_PROFILE = "/profiles/error-profile"



APIARY_PROFILES_URL = "http://docs.bloodalert.apiary.io/#reference/profiles/"
APIARY_RELS_URL = "http://docs.bloodalert.apiary.io/#reference/link-relations/"

NAMESPACE="bloodalert"
LINK_RELATIONS_URL = "/bloodalart/link-relations/"

#Define the application and the api
app = Flask(__name__) #, static_folder="static", static_url_path="/."
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)


app.config.update({"Engine": database.Engine()})

#DB_PATH = 'db/bloodAlert.db'
#app.config.update({"Engine": database.Engine(DB_PATH)}) # for debugging

#Start the RESTful API.
api = Api(app)

# These two classes below are how we make producing the resource representation
# JSON documents manageable and resilient to errors. As noted, our mediatype is
# Mason. Similar solutions can easily be implemented for other mediatypes.

class MasonObject(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)        
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
#ERROR HANDLERS

def create_error_response(status_code, title, message=None):
    """ 
    Creates a: py: class:`flask.Response` instance when sending back an
    HTTP error response

    : param integer status_code: The HTTP status code of the response
    : param str title: A short description of the problem
    : param message: A long description of the problem
    : rtype:: py: class:`flask.Response`
    """

    resource_url = None
    #We need to access the context in order to access the request.path
    ctx = _request_ctx_stack.top
    if ctx is not None:
        resource_url = request.path
    envelope = MasonObject(resource_url=resource_url)
    envelope.add_error(title, message)

    return Response(json.dumps(envelope), status_code, mimetype=MASON+";"+ERROR_PROFILE)

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found",
                                 "This resource url does not exit")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error",
                    "The system has failed. Please, contact the administrator")

@app.before_request
def connect_db():
    """
    Creates a database connection before the request is proccessed.

    The connection is stored in the application context variable flask.g .
    Hence it is accessible from the request object.
    """

    g.con = app.config["Engine"].connect()

#HOOKS
@app.teardown_request
def close_connection(exc):
    """ 
    Closes the database connection
    Check if the connection is created. It migth be exception appear before
    the connection is created.
    """

    if hasattr(g, "con"):
        g.con.close()

        
#Add the Regex Converter so we can use regex expressions when we define the
#routes
app.url_map.converters["regex"] = RegexConverter
    
# End of Imported code

class BloodAlertObject(MasonObject):    
    """
    A convenience subclass of MasonObject that defines a bunch of shorthand 
    methods for inserting application specific objects into the document. This
    class is particularly useful for adding control objects that are largely
    context independent, and defining them in the resource methods would add a 
    lot of noise to our code - not to mention making inconsistencies much more
    likely!

    In the bloodalert code this object should always be used for root document as 
    well as any items in a collection type resource. 
    """

    def __init__(self, **kwargs):
        """
        Calls dictionary init method with any received keyword arguments. Adds
        the controls key afterwards because hypermedia without controls is not 
        hypermedia. 
        """

        super(BloodAlertObject, self).__init__(**kwargs)
        self["@controls"] = {}
        
    

    def add_control_blood_banks_all(self):
        """
        Adds the blood-banks-all link to an object. 
        """

        self["@controls"]["bloodalert:blood-banks-all"] = {
            "href": api.url_for(BloodBanks),
            "title": "List all blood banks"
        }

    def add_control_donors_all(self):
        """
        Adds the donor-all control to an object. 
        """

        self["@controls"]["bloodalert:donors-all"] = {
            "href": api.url_for(BloodDonors),
            "title": "List all blood donors"
        }

    def add_control_blood_types_all(self):
        """
        Adds the blood-types-all control to an object. 
        """

        self["@controls"]["bloodalert:blood-types-all"] = {
            "href": api.url_for(BloodTypes),
            "title": "List all blood types"
        }
    def add_control_blood_donor_history_list(self,donorId):
        """
        Adds the blood-donor-history-list control to an object. 
        """

        self["@controls"]["bloodalert:blood-donor-history-list"] = {
            "href": api.url_for(BloodDonorHistoryList,donorId=donorId),
            "title": "List the donation history of this blood donor"
        }

    def add_control_blood_bank_history_list(self,bloodBankId):
        """
        Adds the blood-bank-history-list control to an object. 
        """

        self["@controls"]["bloodalert:blood-bank-history-list"] = {
            "href": api.url_for(BloodBankHistoryList,bloodBankId=bloodBankId),
            "title": "List History of this blood bank",
            "method": "GET"
        }

    def add_control_add_blood_bank(self):
        """
        This adds the add-blood-bank control to an object. Intended for the  
        document object. 
        """

        self["@controls"]["bloodalert:add-blood-bank"] = {
            "href": api.url_for(BloodBanks),
            "title": "Add Blood Bank",
            "encoding": "json",
            "method": "POST",
            "schema": self._blood_bank_schema()
        }
    def add_control_add_blood_donor(self):
        """
        This adds the add-blood-donor control to an object.  
        """
        self["@controls"]["bloodalert:add-blood-donor"] = {
            "href": api.url_for(BloodDonors),
            "title": "Add Blood Donor",
            "encoding": "json",
            "method": "POST",
            "schema": self._blood_donor_schema()
        }

    def add_control_add_blood_type(self):
        """
        This adds the add-blood-type control to an object. 
        """

        self["@controls"]["bloodalert:add-blood-type"] = {
            "href": api.url_for(BloodTypes),
            "title": "Add Blood Type",
            "encoding": "json",
            "method": "POST",
            "schema": self._blood_type_schema()
        }
    def add_control_blood_donor_donate(self,donorId):
        """
        This adds the blood-donor-donate control to an object. 
        """

        self["@controls"]["bloodalert:blood-donor-donate"] = {
            "href": api.url_for(BloodDonorHistoryList,donorId=donorId),
            "title": "Add Blood Donation",
            "encoding": "json",
            "method": "POST",
            "schema": self._blood_donor_history_schema()
        }
    def add_control_delete_blood_bank(self, bloodBankId):
        """
        Adds the delete control to Blood Bank object.

        : param str bloodBankId:bloodBankId in the bbank-N format, where N is a number
        """

        self["@controls"]["bloodalert:delete"] = {
            "href": api.url_for(BloodBank, bloodBankId=bloodBankId),  
            "title": "Delete this Blood Bank",
            "method": "DELETE"
        }

    def add_control_blood_bank_blood_level(self, bloodBankId):
        """
        Adds the blood bank blood level control to Blood Bank object.

        : param str bloodBankId:bloodBankId in the bbank-N format, where N is a number
        """

        self["@controls"]["bloodalert:blood-bank-blood-level"] = {
            "href": api.url_for(BloodBankBloodLevels, bloodBankId=bloodBankId),  
            "title": "List Blood levels of this Blood Bank",
            "method": "GET"
        }
    def add_control_blood_bank_blood_level_parent(self,bloodBankId):
        """
        Adds the blood bank blood level parent control to Blood Bank blood level object.

        : param str bloodBankId:bloodBankId in the bbank-N format, where N is a number
        """

        self["@controls"]["parent"] = {
            "href": api.url_for(BloodBank, bloodBankId=bloodBankId),  
            "title": "The related blood bank",
            "method": "GET"
        }

    def add_control_delete_blood_donor(self, donorId):
       """
        Adds the delete control to Blood Donor object.

        : param str donorId: donorId in the bdonor-N format, where N is a number
       """
       
       self["@controls"]["bloodalert:delete"] = {
            "href": api.url_for(BloodDonor, donorId=donorId),  
            "title": "Delete this Blood Donor",
            "method": "DELETE"
        }
    def add_control_delete_blood_donor_donation(self, donorId,historyId):
       """
        Adds the delete control to Blood donor donation object.

        : param str donorId: donorId in the bdonor-N format, where N is a number
        : param str historyId: blood donor donation id in the history-N form, where N is a number
       """
       
       self["@controls"]["bloodalert:delete"] = {
            "href": api.url_for(BloodDonorHistory, donorId=donorId,historyId=historyId),  
            "title": "Delete this Blood Donor donation",
            "method": "DELETE"
        }
    def add_control_delete_blood_bank_history(self, bloodBankId,historyId):
        """
        Adds the delete control to Blood bank history object.

        : param str bloodBankId: bloodBankId in the bbank-N format, where N is a number
        : param str historyId: blood bank history id in the history-N form, where N is a number
       """
        self["@controls"]["bloodalert:delete"] = {
            "href": api.url_for(BloodBankHistory, bloodBankId=bloodBankId,historyId=historyId),    
            "title": "Delete this Blood Bank history",
            "method": "DELETE"
        }      

    def add_control_delete_blood_type(self,btypeId):
        """
        Adds the delete control to Blood Bank object.
        
        : param str btypeId:btypeId in the btype-N format, where N is a number
        """
       
        self["@controls"]["bloodalert:delete"] = {
            "href": api.url_for(BloodType, bloodTypeId=btypeId),  
            "title": "Delete this Blood type",
            "method": "DELETE"
        }

    
    def add_control_edit_blood_type(self,btypeId):
        """
        Adds the edit control to a blood type object. 

        : param str btypeId: blood type id in the btype-N form, where N is a number
        """

        self["@controls"]["bloodalert:edit"] = {
            "href": api.url_for(BloodType, bloodTypeId=btypeId),
            "title": "Edit this Blood Type",
            "encoding": "json",
            "method": "PUT",
            "schema": self._blood_type_schema()
        }

    def add_control_edit_blood_bank(self,bloodBankId):
        """
        Adds the edit control to a blood bank object. 

        : param str bloodBankId: blood bank id in the bbank-N form, where N is a number
        """

        self["@controls"]["bloodalert:edit"] = {
            "href": api.url_for(BloodBank, bloodBankId=bloodBankId),
            "title": "Edit this Blood Bank",
            "encoding": "json",
            "method": "PUT",
            "schema": self._blood_bank_schema(edit=True)
        }
    def add_control_edit_blood_bank_history(self,bloodBankId,historyId):
        """
        Adds the edit control to a blood bank history object. 

        : param str bloodBankId: blood bank id in the bbank-N form, where N is a number
        : param str historyId: blood bank history id in the history-N form, where N is a number
        """

        self["@controls"]["bloodalert:edit"] = {
            "href": api.url_for(BloodBankHistory, bloodBankId=bloodBankId,historyId=historyId),
            "title": "Edit this Blood Bank History",
            "encoding": "json",
            "method": "PUT",
            "schema": self._blood_bank_history_schema(edit=True)
        }
    def add_control_edit_blood_donor(self,donorId):
        """
        Adds the edit control to a blood donor object. 

        : param str donorId: blood donor id in the bdonor-N form, where N is a number
        """

        self["@controls"]["bloodalert:edit"] = {
            "href": api.url_for(BloodDonor, donorId=donorId),
            "title": "Edit this Blood Donor",
            "encoding": "json",
            "method": "PUT",
            "schema": self._blood_donor_schema(edit=True)
        }
    def add_control_edit_blood_donor_donation(self,donorId,historyId):
        """
        Adds the edit control to a blood donor object. 

        : param str donorId: blood donor id in the bdonor-N form, where N is a number
        : param str historyId: blood donor donation id in the history-N form, where N is a number
        """

        self["@controls"]["bloodalert:edit"] = {
            "href": api.url_for(BloodDonorHistory, donorId=donorId,historyId=historyId),
            "title": "Modify Blood Donation",
            "encoding": "json",
            "method": "PUT",
            "schema": self._blood_donor_history_schema(edit=True)
        }
    def _blood_type_schema(self):
        """
        Creates a schema dictionary for Blood Type.
        
        : rtype:: dict
        """
        schema = {
            "type": "object",
            "properties": {}
        }
        
        props = schema["properties"]
  

        props["name"] = {
            "title": "Name",
            "description": "The blood type's name",
            "type": "string"
        }

        schema["required"]=["name"]

        return schema

    def _blood_bank_schema(self, edit=False):
        """
        Creates a schema dictionary for Blood Bank. If we're editing a blood bank
        some attributes are not required. If we're adding a new blood bank, some attributes are 
        required . This is controlled by the edit flag.

        : param bool edit: is this schema for an edit 
        : rtype:: dict
        """
       

        schema = {
            "type": "object",
            "properties": {}
        }
        
        props = schema["properties"]

        if not edit:
            schema["required"]=["name", "city","telephone","email","threshold"]
        else:
            schema["required"]=[]   

        props["name"] = {
            "title": "Name",
            "description": "The blood bank's name",
            "type": "string"
        }
        props["address"] = {
            "title": "Address",
            "description": "The blood bank's address",
            "type": "string",
            "default": "-"
        }
        props["city"] = {
            "title": "City",
            "description": "The blood bank's city",
            "type": "string"
        }
        props["telephone"] = {
            "title": "Telephone",
            "description": "The blood bank's telephone",
            "type": "string"
        }
        props["email"] = {
            "title": "Email",
            "description": "The blood bank's email",
            "type": "string"
        }
        props["latitude"] = {
            "title": "Latitude",
            "description": "The blood bank's latitude",
            "type": "number"
        }
        props["longitude"] = {
            "title": "Longitude",
            "description": "The blood bank's longitude",
            "type": "number"
        }
        props["threshold"] = {
            "title": "Threshold",
            "description": "The blood bank's threshold of blood level to alert",
            "type": "number"
        }

        return schema
    
    def _blood_donor_history_schema(self,edit=False):
        """
        Creates a schema dictionary for Blood Donor donation History.         
        : rtype:: dict
        """
        schema = {
            "type": "object",
            "properties": {}
        }

        if not edit:

            schema["required"]=["bloodTypeId", "bloodBankId", "amount"]
        else:
            schema["required"]=[]

        props = schema["properties"]

        props["bloodTypeId"]= {
            "title": "Blood Type",
            "description": "The blood donor's bloodTypeId",
            "type": "string"
          }
         
        props["bloodBankId"] ={
            "title": "Blood bank",
            "description": "The blood bank of the blood donation",
            "type": "string"
          }
        props["amount"]= {
            "title": "Amount of Blood donated",
            "description": "The amount of blood donated",
            "type": "number"
          }
        props["timeStamp"]= {
            "title": "Time of Donation",
            "description": "The timeStamp of blood donated",
            "type": "string"
          }
        return schema

    def _blood_bank_history_schema(self,edit=False):
        """
        Creates a schema dictionary for Blood Bank donation History.         
        : rtype:: dict
        """
        schema = {
            "type": "object",
            "properties": {}
        }

        if not edit:

            schema["required"]=["donorId", "bloodTypeId", "amount"]
        else:
            schema["required"]=[]

        props = schema["properties"]

        props["donorId"] ={
            "title": "Blood donor",
            "description": "The blood donor's id",
            "type": "string"
          }

        props["bloodTypeId"]= {
            "title": "Blood Type",
            "description": "The blood donor's bloodTypeId",
            "type": "string"
          }
         
        props["amount"]= {
            "title": "Amount of Blood donated",
            "description": "The amount of blood donated",
            "type": "number"
          }
        props["timeStamp"]= {
            "title": "Time of Donation",
            "description": "The timeStamp of blood bank history",
            "type": "string"
          }
        props["tag"]= {
            "title": "Tag",
            "description": "The tag of donation history",
            "type": "string",
            "default": "DONATION"
          }
        return schema

    def _blood_donor_schema(self, edit=False):
        """
        Creates a schema dictionary for Blood Donor. If we're editing a blood donor
        some attributes are not required. If we're adding a new blood donor, some attributes are 
        required . This is controlled by the edit flag.

        : param bool edit: is this schema for an edit 
        : rtype:: dict
        """
        schema = {
            "type": "object",
            "properties": {}
        }
        
        props = schema["properties"]

        if not edit:
            schema["required"]=["firstName","familyName",  "birthDate","gender","bloodTypeId",\
                                 "telephone",  "address","email"]
        else:
            schema["required"]=[]  

        props["firstname"]={
            "title": "FirstName",
            "description": "The blood donor's firstname",
            "type": "string"
          }

        props["familyname"]= {
            "title": "Family Name",
            "description": "The blood donor's familyname",
            "type": "string"
          }

        props["birthDate"]= {
            "title": "Birth Date",
            "description": "The blood donor's birth Date",
            "type": "string"
          }

        props["gender"]= {
            "title": "Gender",
            "description": "The blood donor's gender",
            "type": "string"
          }
          
        props["bloodTypeId"]= {
            "title": "Blood Type",
            "description": "The blood donor's bloodType Id",
            "type": "string"
          }

        props["telephone"]= {
            "title": "Telephone",
            "description": "The blood donor's telephone",
            "type": "string"
          }
        props["city"]= {
            "title": "City",
            "description": "The blood donor's city",
            "type": "string"
          }
          
        props["address"]= {
            "title": "Address",
            "description": "The blood donor's address",
            "type": "string"
          }
        props["email"] ={
            "title": "Email",
            "description": "The blood donor's email",
            "type": "string"
          }
        
        return schema


class BloodBanks(Resource):
    """
    Resource Blood Banks Implementation
    """
    def get(self):
        """
        Gets a list of all blood banks

        INPUT parameters:
          None
        
        RESPONSE STATUS CODE:
         * Returns 200 Blood Bank list loaded successfully.
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
        """
        BBanks=g.con.get_blood_banks()
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodBanks))
        output.add_control_add_blood_bank()
        output.add_control_donors_all()
        output.add_control_blood_types_all()

       
        items=output["items"]=[]
        for bank in BBanks:
            
            item=BloodAlertObject()
            item.add_control("self",href=api.url_for(BloodBank,bloodBankId=bank["bloodBankId"]))
            item.add_control("profile",href=BLOODALERT_BLOOD_BANK_PROFILE )
            
            item["bloodBankId"]=bank["bloodBankId"]
            item["name"]=bank["name"]
            item["address"]=bank["address"]
            item["city"]=bank["city"]
            item["telephone"]=bank["telephone"]
            item["email"]=bank["email"]
            item["latitude"]=bank["latitude"]
            item["longitude"]=bank["longitude"]
            item["threshold"]=bank["threshold"]

            items.append(item)
        
        return Response(json.dumps(output),200,mimetype=MASON+";" + BLOODALERT_BLOOD_BANK_PROFILE)


    def post(self):
        """
        Adds a new Blood Bank to the bloodAlert database

        REQUEST ENTITY BODY:
         * Media type: JSON:
         * Profile: Blood Banks
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile

        The body should be a JSON document that matches the schema for new Blood Bank        

        RESPONSE STATUS CODE:
         * Returns 201 if the blood Bank has been added correctly.
           The Location header contains the url of the new blood Bank
         * Returns 400 if the blood Bank is not well formed or the entity body is
           empty.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the blood Bank could not be added to database.
        """

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:
            name=request_body["name"]
            address=request_body["address"]
            city=request_body["city"]
            telephone=request_body["telephone"]
            email=request_body["email"]
            latitude=request_body["latitude"]
            longitude=request_body["longitude"]
            threshold=request_body["threshold"]

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            newBloodBankId=g.con.create_blood_bank(name, city, telephone, email, threshold, address, latitude, longitude)
        except Exception as ex:
            return create_error_response(500, "Blood bank could not be created",
                                         "Cannot create the blood bank in the database - {}".format(ex.message))
        if not newBloodBankId:
            return create_error_response(500, "Blood bank could not be created",
                                         "Cannot create the blood bank in the database")

        url=api.url_for(BloodBank,bloodBankId=newBloodBankId)

        return Response(status= 201,headers={"Location": url})



class BloodBank(Resource):
    """
    Blood Bank Resource Implementation
    """
    def get(self,bloodBankId):
        """
        Gets a blood bank information in the database

        INPUT:
            The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
        
        RESPONSE STATUS CODE:
             * Returns 200 if blood bank information loaded successfully
             * Returns 404 if no such blood bank with specified id

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
        """

        
        try:
            bank = g.con.get_blood_bank(bloodBankId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood bank",
                                            "No such blood bank with specified {} - {}".format(bloodBankId, ex.message))

       
        if bank is None or not bank:
            return create_error_response(404, "No such Blood bank",
                                         "No such blood bank with specified - {}".format(bloodBankId)
                                         )
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodBank,bloodBankId=bloodBankId))
        output.add_control("profile",href=BLOODALERT_BLOOD_BANK_PROFILE )
        output.add_control("collection",href=api.url_for(BloodBanks))
        output.add_control_delete_blood_bank(bloodBankId)
        output.add_control_edit_blood_bank(bloodBankId)
        output.add_control_blood_bank_history_list(bloodBankId)
        output.add_control_blood_bank_blood_level(bloodBankId)
    
        output["bloodBankId"]=bank["bloodBankId"]
        output["name"]=bank["name"]
        output["address"]=bank["address"]
        output["city"]=bank["city"]
        output["telephone"]=bank["telephone"]
        output["email"]=bank["email"]
        output["latitude"]=bank["latitude"]
        output["longitude"]=bank["longitude"]
        output["threshold"]=bank["threshold"]

        return Response(json.dumps(output), 200, mimetype=MASON+";" + BLOODALERT_BLOOD_BANK_PROFILE)

    def put(self,bloodBankId):
        """
       Modifies a blood bank

        INPUT:
            The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
        
        RESPONSE STATUS CODE:
             * Returns 204 if the blood bank is modified sucessfully
             * Returns 400 if the blood bank is malformed or the entity body is
                empty.
             * Returns 415 if the format of the response is not json
             * Returns 404 if no blood bank with bloodBankId exist on database
             * Returns 500 if the blood bank could not be modified

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
       
        """

        if not g.con.get_blood_bank(bloodBankId):
            return create_error_response(404, "No such Blood bank",
                                         "No such blood bank with id %s" % bloodBankId
                                        )

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")

        request_body = request.get_json(force=True)

        try:
            name=request_body.get("name",None)
            address=request_body.get("address",None)
            city=request_body.get("city",None)
            telephone=request_body.get("telephone",None)
            email=request_body.get("email",None)
            latitude=request_body.get("latitude",None)
            longitude=request_body.get("longitude",None)           
            threshold=request_body.get("threshold",None)

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            editedBloodBankId=g.con.modify_blood_bank(bloodBankId, name, address, city, email, telephone, latitude, longitude, threshold)
        except Exception as ex:
            return create_error_response(500, "Blood bank could not be modified",
                                         "Blood bank with id {} could not be modified - {}".format(bloodBankId, ex.message))
        if not editedBloodBankId:
            return create_error_response(500, "Blood bank could not be modified",
                                         "Blood bank with id {} could not be modified".format(bloodBankId))
        else:
            return "", 204

    def delete(self,bloodBankId):
        """
        Deletes a Blood bank from the Blood Alert database.

       INPUT:
            The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
        
        RESPONSE STATUS CODE
         * Returns 204 if the blood bank was deleted
         * Returns 404 if the bloodBankId is not associated to any blood bank.

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile

        
        """

        if g.con.delete_blood_bank(bloodBankId):
            return "", 204
        else:            
            return create_error_response(404, "No such Blood bank",
                                         "No such blood bank with id %s" % bloodBankId
                                        )
class BloodBankBloodLevels(Resource):
    """
    Resource Blood Bank Blood Levels implementation 
    """
    def get(self,bloodBankId):
        """
        Get blood levels of a blood bank

        INPUT:
            The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
        
        RESPONSE STATUS CODE:
             * Returns 200 if blood level information loaded successfully
             * Returns 404 if no such blood bank with specified id

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
        """

        
        try:
            bloodLevels = g.con.get_blood_bank_blood_level(bloodBankId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood bank",
                                            "No such blood bank with specified {} - {}".format(bloodBankId, ex.message))

       
        if bloodLevels is None or not bloodLevels:
            return create_error_response(404, "No such Blood bank",
                                         "No such blood bank with specified - {}".format(bloodBankId)
                                         )
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodBankBloodLevels,bloodBankId=bloodBankId))
        
        output.add_control_blood_bank_blood_level_parent(bloodBankId)    

        items=output["items"]=[]
        for level in bloodLevels:
            
            item=BloodAlertObject()
            
            item.add_control("profile",href=BLOODALERT_BLOOD_BANK_PROFILE)            
            item.add_control("bloodType",href=api.url_for(BloodType,bloodTypeId=level["bloodTypeId"]))
            item["bloodTypeName"]=level["bloodTypeName"]
            item["amount"]=level["amount"] 
            item["bloodTypeId"]=level["bloodTypeId"]           

            items.append(item)
        
        return Response(json.dumps(output),200,mimetype=MASON+";" + BLOODALERT_BLOOD_BANK_PROFILE)
    
class BloodBankHistoryList(Resource):
    """
    Resource Blood Bank History List Implementation
    """
    def get(self, bloodBankId):
        """
        Gets a list of all blood bank history

        INPUT 
        The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
        
        
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
        """
        donations=g.con.get_blood_bank_histories(bloodBankId)
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodBankHistoryList,bloodBankId=bloodBankId))
        output.add_control_blood_bank_blood_level(bloodBankId)
        

       
        items=output["items"]=[]
        for donation in donations:
            
            item=BloodAlertObject()
            item.add_control("self",href=api.url_for(BloodBankHistory,bloodBankId=donation["bloodBankId"],historyId=donation["historyId"]))
            item.add_control("profile",href=BLOODALERT_BLOOD_BANK_PROFILE )
            item.add_control("bloodtype",href=api.url_for(BloodType,bloodTypeId=donation["bloodTypeId"]))
            item.add_control("donor",href=api.url_for(BloodDonor,donorId=donation["donorId"]))
            item.add_control("bloodbank",href=api.url_for(BloodBank,bloodBankId=donation["bloodBankId"]))
            
            item["historyId"]=donation["historyId"]
            item["donorId"]=donation["donorId"]
            item["bloodTypeId"]=donation["bloodTypeId"]
            item["bloodBankId"]=donation["bloodBankId"]           
            item["amount"]=donation["amount"]
            item["timeStamp"]=donation["timeStamp"]
            item["tag"]=donation["tag"]

            items.append(item)
        
        return Response(json.dumps(output),200,mimetype=MASON+";" + BLOODALERT_BLOOD_BANK_PROFILE)

class BloodBankHistory(Resource):
    """
    Resource Blood Bank History Implementation
    """
    def get(self,bloodBankId,historyId):
        """
        Gets a bank history

        INPUT 
        The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
             * historyId: Id of the the blood donation history in the format history-\d{1,3} Example: history-1.
        
        RESPONSE STATUS CODE:
             * Returns 200 if the list can be generated and it is not empty
             * Returns 404 if no blood bank meets the requirement
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
        * Profile: Blood Bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
        """
        try:
            bank = g.con.get_blood_bank(bloodBankId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood bank",
                                            "No such blood bank with specified {} - {}".format(bloodBankId, ex.message))

       
        if bank is None or not bank:
            return create_error_response(404, "No such Blood bank",
                                         "No such blood bank with specified - {}".format(bloodBankId)
                                         )
        try:
            history = g.con.get_history(historyId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood bank donation history",
                                            "No such blood bank nation history with specified {} - {}".format(historyId, ex.message))

       
        if history is None or not history:
            return create_error_response(404, "No such Blood bank donation history",
                                         "No such blood bank nation history with specified - {}".format(historyId)
                                         )
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodBankHistory,bloodBankId=history["bloodBankId"],historyId=history["historyId"]))
        output.add_control("profile",href=BLOODALERT_BLOOD_BANK_PROFILE )
        output.add_control("bloodtype",href=api.url_for(BloodType,bloodTypeId=history["bloodTypeId"]))
        output.add_control("donor",href=api.url_for(BloodDonor,donorId=history["donorId"]))
        output.add_control("bloodbank",href=api.url_for(BloodBank,bloodBankId=history["bloodBankId"]))
        output.add_control_edit_blood_bank_history(bloodBankId,historyId)
        output.add_control_delete_blood_bank_history(bloodBankId,historyId)
        output.add_control_blood_bank_history_list(bloodBankId)
        output.add_control_blood_bank_blood_level(bloodBankId)

        output["historyId"]=history["historyId"]
        output["donorId"]=history["donorId"]           
        output["bloodTypeId"]=history["bloodTypeId"]
        output["bloodBankId"]=history["bloodBankId"]
        output["amount"]=history["amount"]
        output["timeStamp"]=history["timeStamp"]
        output["tag"]=history["tag"]

        return Response(json.dumps(output), 200, mimetype=MASON+";" + BLOODALERT_BLOOD_BANK_PROFILE)
    
    def put(self,bloodBankId,historyId):
        """
        Modifies a blood bank history

        INPUT:
            The query parameters are:
             * bloodBankId: Id of the blood bank in the format bbank-\d{1,3} Example: bbank-1.
             * historyId: Id of the the blood donation history in the format history-\d{1,3} Example: history-1.
        
        RESPONSE STATUS CODE:
             * Returns 204 if the blood bank history is modified sucessfully
             * Returns 400 if the blood bank history is not well formed or the entity body is
                empty.
             * Returns 415 if the format of the response is not json
             * Returns 404 if no blood bank meets the requirement
             * Returns 500 if the blood bank could not be modified

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Bank
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile
       
        """

        try:
            bank = g.con.get_blood_bank(bloodBankId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood bank",
                                            "No such blood bank with specified {} - {}".format(bloodBankId, ex.message))

       
        if bank is None or not bank:
            return create_error_response(404, "No such Blood bank",
                                         "No such blood bank with specified - {}".format(bloodBankId)
                                         )
        try:
            history = g.con.get_history(historyId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood bank history",
                                            "No such blood bank nation history with specified {} - {}".format(historyId, ex.message))

       
        if history is None or not history:
            return create_error_response(404, "No such Blood bank history",
                                         "No such blood bank nation history with specified - {}".format(historyId)
                                         )
        request_body = request.get_json(force=True)

        try:
            donorId=request_body.get("donorId",None)
            bloodTypeId=request_body.get("bloodTypeId",None)
            amount=request_body.get("amount",None)
            timeStamp=request_body.get("timeStamp",None)            

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            editedBloodBankHistoryId=g.con.modify_history( historyId, donorId=donorId, bloodTypeId=bloodTypeId, amount=amount, timeStamp=timeStamp)
        except Exception as ex:
            return create_error_response(500, "Blood bank history could not be modified",
                                         "Blood bank history with id {} could not be modified - {}".format(historyId, ex.message))
        if not editedBloodBankHistoryId:
            return create_error_response(500, "Blood bank history could not be modified",
                                         "Blood bank history with id {} could not be modified".format(historyId))
        else:
            return "", 204

    def delete(self,bloodBankId, historyId):
        """
        Deletes a Blood bank history from the Blood Alert database.

       INPUT:
            The query parameters are:
             * historyId: Id of the blood bank history in the format history-\d{1,3} Example: history-1.
        
        RESPONSE STATUS CODE
         * Returns 204 if the blood bank history record was deleted
         * Returns 404 if the historyId is not associated to any blood donor.

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
        * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-bank-profile

        """

        if g.con.delete_history(historyId):
            return "", 204
        else:            
            return create_error_response(404, "No such blood bank history record",
                                         "No such blood bank history with id %s" % historyId
                                        )


class BloodDonors(Resource):
    """
    Resource Blood Donors Implementation
    """
    def get(self):
        """
        Gets a list of all blood donors

        INPUT parameters:
          None
        
        
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile
        """
        donors=g.con.get_blood_donors()
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodDonors))
        output.add_control_add_blood_donor()
        output.add_control_blood_banks_all()
        output.add_control_blood_types_all()

       
        items=output["items"]=[]
        for donor in donors:
            
            item=BloodAlertObject()
            item.add_control("self",href=api.url_for(BloodDonor,donorId=donor["donorId"]))
            item.add_control("profile",href=BLOODALERT_BLOOD_DONOR_PROFILE )
            item.add_control("bloodtype",href=api.url_for(BloodType,bloodTypeId=donor["bloodTypeId"]))
            
            item["donorId"]=donor["donorId"]
            item["firstname"]=donor["firstname"]
            item["familyName"]=donor["familyName"]
            item["birthDate"]=donor["birthDate"]
            item["gender"]=donor["gender"]
            item["bloodTypeId"]=donor["bloodTypeId"]
            item["telephone"]=donor["telephone"]
            item["city"]=donor["city"]
            item["address"]=donor["address"]
            item["email"]=donor["email"]

            items.append(item)
        
        return Response(json.dumps(output),200,mimetype=MASON+";" + BLOODALERT_BLOOD_DONOR_PROFILE)
    def post(self):
        """
        Adds a new Blood Donor to the bloodAlert database

        REQUEST ENTITY BODY:
         * Media type: JSON:
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile

        The body should be a JSON document that matches the schema for new Blood Donor        

        RESPONSE STATUS CODE:
         * Returns 201 if the blood donor has been added correctly.
           The Location header contains the url of the new blood donor
         * Returns 400 if the blood donor is not well formed or the entity body is
           empty.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the blood donor could not be added to database.
        """

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:

            firstname=request_body["firstname"]
            familyName=request_body["familyName"]
            telephone=request_body["telephone"]
            email=request_body["email"]
            bloodTypeId=request_body["bloodTypeId"]
            birthDate=request_body["birthDate"]
            gender=request_body["gender"]

            #optional attributes
            address=request_body.get("address","-")
            city=request_body.get("city",None)

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            newBloodDonorId=g.con.create_blood_donor(firstname,familyName, telephone, email,bloodTypeId, birthDate, gender, address,city)
        except Exception as ex:
            return create_error_response(500, "Blood donor could not be created",
                                         "Cannot create the blood donor in the database - {}".format(ex.message))
        if not newBloodDonorId:
            return create_error_response(500, "Blood donor could not be created",
                                         "Cannot create the blood donor in the database")

        url=api.url_for(BloodDonor,donorId=newBloodDonorId)

        return Response(status= 201,headers={"Location": url})
        

class BloodDonor(Resource):
    """
    Blood Donor Resource Implementation
    """
    def get(self,donorId):
        """
        Gets a blood donor information in the database

        INPUT:
            The query parameters are:
             * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
        
        RESPONSE STATUS CODE:
             * Returns 200 if the list can be generated and it is not empty
             * Returns 404 if no blood donor meets the requirement

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile
        """

        
        try:
            donor = g.con.get_blood_donor(donorId)
        except (ValueError,Exception) as ex:
            return create_error_response(404, "No such Blood donor",
                                            "No such blood donor with specified {} - {}".format(donorId, ex.message))

       
        if donor is None or not donor:
            return create_error_response(404, "No such Blood donor",
                                         "No such blood donor with specified - {}".format(donorId)
                                         )
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodDonor,donorId=donorId))
        output.add_control("profile",href=BLOODALERT_BLOOD_DONOR_PROFILE )
        output.add_control("bloodtype",href=api.url_for(BloodType,bloodTypeId=donor["bloodTypeId"]))
        output.add_control("collection",href=api.url_for(BloodDonors))
        output.add_control_delete_blood_donor(donorId)
        output.add_control_edit_blood_donor(donorId)
        output.add_control_blood_donor_history_list(donorId)

        output["donorId"]=donor["donorId"]
        output["firstname"]=donor["firstname"]
        output["familyName"]=donor["familyName"]
        output["birthDate"]=donor["birthDate"]
        output["gender"]=donor["gender"]
        output["bloodTypeId"]=donor["bloodTypeId"]
        output["telephone"]=donor["telephone"]
        output["city"]=donor["city"]
        output["address"]=donor["address"]
        output["email"]=donor["email"]

        return Response(json.dumps(output), 200, mimetype=MASON+";" + BLOODALERT_BLOOD_DONOR_PROFILE)
    
    def put(self,donorId):
        """
            Modifies a blood donor

            INPUT:
                The query parameters are:
                * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
            
            RESPONSE STATUS CODE:
                * Returns 204 if the blood donor is modified sucessfully
                * Returns 400 if the blood donor is not well formed or the entity body is
                    empty.
                * Returns 415 if the format of the response is not json
                * Returns 404 if no blood donor meets the requirement
                * Returns 500 if the blood donor could not be modified

            RESPONSE ENTITY BODY:
            * Media type: Mason
            https://github.com/JornWildt/Mason
            * Profile: Blood Donor
            http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile
        
        """

        if not g.con.get_blood_donor(donorId):
            return create_error_response(404, "No such Blood donor",
                                         "No such blood donor with id %s" % donorId
                                        )

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")

        request_body = request.get_json(force=True)

        try:

            firstname=request_body.get("firstname",None)
            familyName=request_body.get("familyName",None)
            telephone=request_body.get("telephone",None)
            email=request_body.get("email",None)
            bloodTypeId=request_body.get("bloodTypeId",None)
            birthDate=request_body.get("birthDate",None)
            gender=request_body.get("gender",None)           
            address=request_body.get("address",None)
            city=request_body.get("city",None)

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            editedBloodDonorId=g.con.modify_blood_donor(donorId, firstname,familyName, telephone, email,bloodTypeId, birthDate, gender, address,city)
        except Exception as ex:
            return create_error_response(500, "Blood donor could not be modified",
        
                                          "Blood donor with id {} could not be modified - {}".format(donorId, ex.message))
        
        if not editedBloodDonorId:
            return create_error_response(500, "Blood donor could not be modified",
                                         "Blood donor with id {} could not be modified".format(donorId))
        else:
            return "", 204
    def delete(self,donorId):
        """
        Deletes a Blood donor from the Blood Alert database.

       INPUT:
            The query parameters are:
             * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
        
        RESPONSE STATUS CODE
         * Returns 204 if the blood donor was deleted
         * Returns 404 if the donorId is not associated to any blood donor.

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile

        
        """

        if g.con.delete_blood_donor(donorId):
            return "", 204
        else:            
            return create_error_response(404, "No such Blood donor",
                                         "No such blood donor with id %s" % donorId
                                        )
class BloodDonorHistoryList(Resource):
    """
    Resource Blood Donor History List Implementation
    """
    def get(self, donorId):
        """
        Gets a list of all blood donor history

        INPUT 
        The query parameters are:
             * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
        
        
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile
        """
        donations=g.con.get_blood_donor_histories(donorId)
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodDonorHistoryList,donorId=donorId))
        output.add_control_blood_donor_donate(donorId)
        

       
        items=output["items"]=[]
        for donation in donations:
            
            item=BloodAlertObject()
            item.add_control("self",href=api.url_for(BloodDonorHistory,donorId=donation["donorId"],historyId=donation["historyId"]))
            item.add_control("profile",href=BLOODALERT_BLOOD_DONOR_PROFILE )
            item.add_control("bloodtype",href=api.url_for(BloodType,bloodTypeId=donation["bloodTypeId"]))
            item.add_control("donor",href=api.url_for(BloodDonor,donorId=donation["donorId"]))
            item.add_control("bloodbank",href=api.url_for(BloodBank,bloodBankId=donation["bloodBankId"]))
            
            item["historyId"]=donation["historyId"]
            item["donorId"]=donation["donorId"]           
            item["bloodTypeId"]=donation["bloodTypeId"]
            item["bloodBankId"]=donation["bloodBankId"]
            item["amount"]=donation["amount"]
            item["timeStamp"]=donation["timeStamp"]
            item["tag"]=donation["tag"]

            items.append(item)
        
        return Response(json.dumps(output),200,mimetype=MASON+";" + BLOODALERT_BLOOD_DONOR_PROFILE)
    def post(self,donorId):
        """
        Adds a new Blood Donor to the bloodAlert database

        INPUT 
        The query parameters are:
             * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
        
        REQUEST ENTITY BODY:
         * Media type: JSON:
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile

        The body should be a JSON document that matches the schema for new Blood Donor        

        RESPONSE STATUS CODE:
         * Returns 201 if the blood donor donation has been added correctly.
           The Location header contains the url of the new blood donor donation
         * Returns 400 if the blood donor donation is not well formed or the entity body is
           empty.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the blood donor donation could not be added to database.
        """

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:

            amount=request_body["amount"]
            timeStamp=request_body["timeStamp"]            
            bloodBankId=request_body["bloodBankId"]
            bloodTypeId=request_body["bloodTypeId"]            

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:           

            newBloodDonorDonationId=g.con.create_history(bloodTypeId,bloodBankId, amount, timeStamp,donorId)
        except Exception as ex:
            return create_error_response(500, "Blood donor donation could not be created",
                                         "Cannot create the blood donor donation in the database - {}".format(ex.message))
        if not newBloodDonorDonationId:
            return create_error_response(500, "Blood donor donation could not be created",
                                         "Cannot create the blood donor donation in the database")

        url=api.url_for(BloodDonorHistory,donorId=donorId, historyId=newBloodDonorDonationId)

        return Response(status= 201,headers={"Location": url})
class BloodDonorHistory(Resource):
    """
    Resource Blood Donor History Implementation
    """
    def get(self,donorId,historyId):
        """
        Gets a donor history

        INPUT 
        The query parameters are:
             * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
             * historyId: Id of the the blood donation history in the format history-\d{1,3} Example: history-1.
        
        RESPONSE STATUS CODE:
             * Returns 200 if the list can be generated and it is not empty
             * Returns 404 if no blood donor meets the requirement
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
        * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile
        """
        try:
            donor = g.con.get_blood_donor(donorId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood donor",
                                            "No such blood donor with specified {} - {}".format(donorId, ex.message))

       
        if donor is None or not donor:
            return create_error_response(404, "No such Blood donor",
                                         "No such blood donor with specified - {}".format(donorId)
                                         )
        try:
            history = g.con.get_history(historyId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood donor donation history",
                                            "No such blood donor nation history with specified {} - {}".format(historyId, ex.message))

       
        if history is None or not history:
            return create_error_response(404, "No such Blood donor donation history",
                                         "No such blood donor nation history with specified - {}".format(historyId)
                                         )
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodDonorHistory,donorId=history["donorId"],historyId=history["historyId"]))
        output.add_control("profile",href=BLOODALERT_BLOOD_DONOR_PROFILE )
        output.add_control("bloodtype",href=api.url_for(BloodType,bloodTypeId=history["bloodTypeId"]))
        output.add_control("donor",href=api.url_for(BloodDonor,donorId=history["donorId"]))
        output.add_control("bloodbank",href=api.url_for(BloodBank,bloodBankId=history["bloodBankId"]))
        output.add_control_blood_donor_history_list(donorId)
        output.add_control_delete_blood_donor_donation(donorId,historyId)
        output.add_control_edit_blood_donor_donation(donorId,historyId)

        output["historyId"]=history["historyId"]
        output["donorId"]=history["donorId"]           
        output["bloodTypeId"]=history["bloodTypeId"]
        output["bloodBankId"]=history["bloodBankId"]
        output["amount"]=history["amount"]
        output["timeStamp"]=history["timeStamp"]
        output["tag"]=history["tag"]

        return Response(json.dumps(output), 200, mimetype=MASON+";" + BLOODALERT_BLOOD_DONOR_PROFILE)
    
    def put(self,donorId,historyId):
        """
       Modifies a blood donor donation history

        INPUT:
            The query parameters are:
             * donorId: Id of the blood donor in the format bdonor-\d{1,3} Example: bdonor-1.
             * historyId: Id of the the blood donation history in the format history-\d{1,3} Example: history-1.
        
        RESPONSE STATUS CODE:
             * Returns 204 if the blood donor donation history is modified sucessfully
             * Returns 400 if the blood donor donation history is not well formed or the entity body is
                empty.
             * Returns 415 if the format of the response is not json
             * Returns 404 if no blood donor meets the requirement
             * Returns 500 if the blood donor could not be modified

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile
       
        """

        try:
            donor = g.con.get_blood_donor(donorId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood donor",
                                            "No such blood donor with specified {} - {}".format(donorId, ex.message))

       
        if donor is None or not donor:
            return create_error_response(404, "No such Blood donor",
                                         "No such blood donor with specified - {}".format(donorId)
                                         )
        try:
            history = g.con.get_history(historyId)
        except ValueError as ex:
            return create_error_response(404, "No such Blood donor donation history",
                                            "No such blood donor nation history with specified {} - {}".format(historyId, ex.message))

       
        if history is None or not history:
            return create_error_response(404, "No such Blood donor donation history",
                                         "No such blood donor nation history with specified - {}".format(historyId)
                                         )
        request_body = request.get_json(force=True)

        try:

            bloodBankId=request_body.get("bloodBankId",None)
            amount=request_body.get("amount",None)
            timeStamp=request_body.get("timeStamp",None)            

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            editedBloodDonorHistoryId=g.con.modify_history( historyId, bloodBankId=bloodBankId, amount=amount, timeStamp=timeStamp)
        except Exception as ex:
            return create_error_response(500, "Blood donor donation history could not be modified",
                                         "Blood donor donation history with id {} could not be modified - {}".format(historyId, ex.message))
        if not editedBloodDonorHistoryId:
            return create_error_response(500, "Blood donor donation history could not be modified",
                                         "Blood donor donation history with id {} could not be modified".format(historyId))
        else:
            return "", 204

    def delete(self,donorId,historyId):
        """
        Deletes a Blood donor donation history from the Blood Alert database.

       INPUT:
            The query parameters are:
             * historyId: Id of the blood donor donation history in the format history-\d{1,3} Example: history-1.
        
        RESPONSE STATUS CODE
         * Returns 204 if the blood donor was deleted
         * Returns 404 if the donorId is not associated to any blood donor.

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
        * Profile: Blood Donor
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-donor-profile

        """

        if g.con.delete_history(historyId):
            return "", 204
        else:            
            return create_error_response(404, "No such Blood donor donation history",
                                         "No such blood donor donation history with id %s" % historyId
                                        )
class BloodTypes(Resource):
    """
    Blood Types Resource Implementation
    """
    def get(self):
        """
        Gets a list of all blood types

        INPUT parameters:
          None       
        
             
        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Type 
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-types-profile
        """

        bloodTypes=g.con.get_blood_types()

        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)
        output.add_control("self",href=api.url_for(BloodTypes))
        output.add_control_add_blood_type()
        output.add_control_donors_all()
        output.add_control_blood_banks_all()
        
        items=output["items"]=[]
        
        for bloodType in bloodTypes:

            item=BloodAlertObject()
            item.add_control("self",href=api.url_for(BloodType,bloodTypeId=bloodType["bloodTypeId"]))
            item.add_control("profile",href=BLOODALERT_BLOOD_TYPES_PROFILE)
            
            item["name"]=bloodType["name"]
            item["bloodTypeId"]=bloodType["bloodTypeId"]

            items.append(item)

        return Response(json.dumps(output),200,mimetype=MASON+";" + BLOODALERT_BLOOD_TYPES_PROFILE)    


    def post(self):
        """
        Adds a new Blood Type to the bloodAlert database

        REQUEST ENTITY BODY:
         * Media type: JSON:
         * Profile: Blood Type
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-types-profile

        The body should be a JSON document that matches the schema for new Blood Type        

        RESPONSE STATUS CODE:
         * Returns 201 if the blood type has been added correctly.
           The Location header contains the url of the new blood type
         * Returns 400 if the blood type is not well formed or the entity body is
           empty.
         * Returns 415 if the format of the response is not json
         * Returns 500 if the blood type could not be added to database.
        """

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")
        request_body = request.get_json(force=True)

        try:
            name=request_body["name"]         

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            newBloodTypeId=g.con.create_blood_type(name)
        except Exception as ex:
            return create_error_response(500, "Blood Type could not be created",
                                         "Cannot create the blood type in the database - {}".format(ex.message))
        if not newBloodTypeId:
            return create_error_response(500, "Blood type could not be created",
                                         "Cannot create the blood donor in the database")

        url=api.url_for(BloodType,bloodTypeId=newBloodTypeId)

        return Response(status= 201,headers={"Location": url})



class BloodType(Resource):
    """
    Blood Type Resource Implementation
    """
    def get(self,bloodTypeId):
        """
        Gets a blood type information in the database

        INPUT:
            The query parameters are:
             * bloodTypeId: Id of the blood type in the format btype-\d{1,3} Example: btype-1.
        
        RESPONSE STATUS CODE:
             * Returns 200 if the list can be generated and it is not empty
             * Returns 404 if no blood type meets the requirement

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
         * Profile: Blood Type
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-types-profile
        """

        
        try:
            bloodType = g.con.get_blood_type(bloodTypeId)
        except (ValueError,Exception) as ex:
            return create_error_response(500, "No such Blood Type",
                                            "No such blood type with specified {} - {}".format(bloodTypeId, ex.message))

       
        if bloodType is None or not bloodType:
            return create_error_response(404, "No such Blood type",
                                         "No such blood type with specified - {}".format(bloodTypeId)
                                         )
        output=BloodAlertObject()
        output.add_namespace(NAMESPACE,LINK_RELATIONS_URL)

        output.add_control("self",href=api.url_for(BloodType,bloodTypeId=bloodTypeId))
        output.add_control("profile",href=BLOODALERT_BLOOD_TYPES_PROFILE )
        output.add_control("collection",href=api.url_for(BloodTypes))
        output.add_control_delete_blood_type(bloodTypeId)
        output.add_control_edit_blood_type(bloodTypeId)
        

        output["bloodTypeId"]=bloodType["bloodTypeId"]
        output["name"]=bloodType["name"]
        

        return Response(json.dumps(output), 200, mimetype=MASON+";" + BLOODALERT_BLOOD_TYPES_PROFILE)

    def put(self,bloodTypeId):
        """        
        Modifies a blood type

        INPUT:
            The query parameters are:
             * typeId: Id of the blood type in the format btype-\d{1,3} Example: btype-1.
        
        RESPONSE STATUS CODE:
             * Returns 204 if the blood type is modified sucessfully
             * Returns 400 if the blood type is not well formed or the entity body is
                empty.
             * Returns 415 if the format of the response is not json
             * Returns 404 if no blood type meets the requirement
             * Returns 500 if the blood type could not be modified

        RESPONSE ENTITY BODY:
        * Media type: Mason
          https://github.com/JornWildt/Mason
        * Profile: Blood type           
           http://docs.bloodalert.apiary.io/#reference/profiles/blood-types-profile
       
        """

        if not g.con.get_blood_type(bloodTypeId):
            return create_error_response(404, "No such Blood type",
                                         "No such blood type with id  %s" % bloodTypeId
                                        )

        if JSON != request.headers.get("Content-Type",""):
            return create_error_response(415, "UnsupportedMediaType",
                                         "Use a JSON compatible format")

        request_body = request.get_json(force=True)

        try:

            name=request_body.get("name",None)            

        except KeyError:
            
            return create_error_response(400, "Wrong request format",
                                         "Be sure to include required body in correct format")
        try:
            editedBloodtypeId=g.con.modify_blood_type(bloodTypeId, name)
        except Exception as ex:
            return create_error_response(500, "Blood type could not be modified",
                                         "Blood type with id {} could not be modified - {}".format(bloodTypeId, ex.message))
        if not editedBloodtypeId:
            return create_error_response(500, "Blood type could not be modified",
                                         "Blood type with id {} could not be modified".format(bloodTypeId))
        else:
            return "", 204
    def delete(self,bloodTypeId):
        """
        Deletes a Blood type from the Blood Alert database.

        INPUT:
                The query parameters are:
                * bloodTypeId: Id of the blood type in the format btype-\d{1,3} Example: btype-1.
            
            RESPONSE STATUS CODE
            * Returns 204 if the blood Type was deleted
            * Returns 404 if the bloodTypeId is not associated to any blood type.

            RESPONSE ENTITY BODY:
            * Media type: Mason
            https://github.com/JornWildt/Mason
            * Profile: Blood type
            http://docs.bloodalert.apiary.io/#reference/profiles/blood-types-profile

        
        """

        if g.con.delete_blood_type(bloodTypeId):
            return "", 204
        else:            
            return create_error_response(404, "No such Blood type",
                                         "No such blood type with id %s" % bloodTypeId
                                        )    

#Define the routes
api.add_resource(BloodBanks, "/bloodalert/bloodbanks/",
                 endpoint="bloodbanks")
api.add_resource(BloodBank, "/bloodalert/bloodbanks/<regex('bbank-\d+'):bloodBankId>/",
                 endpoint="bloodbank")


api.add_resource(BloodBankBloodLevels, "/bloodalert/bloodbanks/<regex('bbank-\d+'):bloodBankId>/bloodlevels/",
                 endpoint="bloodbankbloodlevels")

api.add_resource(BloodDonors, "/bloodalert/donors/",
                 endpoint="blooddonors")
api.add_resource(BloodDonor, "/bloodalert/donors/<regex('bdonor-\d+'):donorId>/",
                 endpoint="blooddonor")

api.add_resource(BloodTypes, "/bloodalert/bloodtypes/",
                 endpoint="bloodtypes")
api.add_resource(BloodType, "/bloodalert/bloodtypes/<regex('btype-\d+'):bloodTypeId>/",
                 endpoint="bloodtype")
api.add_resource(BloodDonorHistoryList,"/bloodalert/donors/<regex('bdonor-\d+'):donorId>/history/",endpoint="blooddonorhistorylist")
api.add_resource(BloodBankHistoryList,"/bloodalert/bloodbanks/<regex('bbank-\d+'):bloodBankId>/history/",endpoint="bloodbankhistorylist")
api.add_resource(BloodDonorHistory,"/bloodalert/donors/<regex('bdonor-\d+'):donorId>/history/<regex('history-\d+'):historyId>/",endpoint="blooddonorhistory")
api.add_resource(BloodBankHistory,"/bloodalert/bloodbanks/<regex('bbank-\d+'):bloodBankId>/history/<regex('history-\d+'):historyId>/",endpoint="bloodbankhistory")

#Redirect profile
@app.route("/profiles/<profile_name>")
@app.route("/profiles/<profile_name>/")
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)

@app.route("/bloodalert/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    return redirect(APIARY_RELS_URL + rel_name)



#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == "__main__":
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
