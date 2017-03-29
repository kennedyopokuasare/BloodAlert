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

        self["@controls"]["bloodalert:blood-type-all"] = {
            "href": api.url_for(BloodTypes),
            "title": "List all blood types"
        }
    def add_control_blood_donor_history_list(self):
        """
        Adds the blood-donor-history-list control to an object. 
        """

        self["@controls"]["bloodalert:blood-donor-history-list"] = {
            "href": "",
            "title": "List the donation history of this blood donor"
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

    def add_control_delete_blood_donor(self, donorId):
       """
        Adds the delete control to Blood Bank object.

        : param str donorId: donorId in the bdonor-N format, where N is a number
       """
       
       self["@controls"]["bloodalert:delete"] = {
            "href": api.url_for(BloodDonor, donorId=donorId),  
            "title": "Delete this Blood Donor",
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
    def _blood_type_schema(self):
        """
        Creates a schema dictionary for Blood Type.

        : param bool edit: is this schema for an edit 
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
            props["required"]=["name", "city","telephone","email","threshold"]
        else:
            props["required"]=[]   

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
            props["required"]=["firstName","familyName",  "birthDate","gender","bloodTypeId",\
                                 "telephone",  "address","email"]
        else:
            props["required"]=[]  

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

class BloodBanks(Resource):
    """
    Resource BloodBanks Implementation 
    """
    def get(self):
        """
        """
       
    def post(self):
        """
        """


class BloodBank(Resource):
    """
    """

class BloodBankBloodLevels(Resource):
    """
    """

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
        except ValueError as ex:
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
        output.add_control_blood_donor_history_list()

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
            address=request_body.get("address","-")
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
    """
class BloodDonorHistory(Resource):
    """
    """

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
        output.add_control_add_blood_bank()
        
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
#Redirect profile
@app.route("/profiles/<profile_name>")
def redirect_to_profile(profile_name):
    return redirect(APIARY_PROFILES_URL + profile_name)

@app.route("/bloodalert/link-relations/<rel_name>/")
def redirect_to_rels(rel_name):
    return redirect(APIARY_RELS_URL + rel_name)

#Send our schema file(s)
@app.route("/bloodalert/schema/<schema_name>/")
def send_json_schema(schema_name):
    return send_from_directory(app.static_folder, "schema/{}.json".format(schema_name))

#Start the application
#DATABASE SHOULD HAVE BEEN POPULATED PREVIOUSLY
if __name__ == "__main__":
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
