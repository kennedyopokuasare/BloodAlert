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


LINK_RELATIONS_URL = "/bloodalart/link-relations/"

#Define the application and the api
app = Flask(__name__) #, static_folder="static", static_url_path="/."
app.debug = True
# Set the database Engine. In order to modify the database file (e.g. for
# testing) provide the database path   app.config to modify the
#database to be used (for instance for testing)
app.config.update({"Engine": database.Engine()})
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

    def add_control_add_blood_bank(self):
        """
        This adds the add-blood-bank control to an object. Intended for the  
        document object. 
        """

        self["@controls"]["bloodalert:add-message"] = {
            "href": api.url_for(BloodBanks),
            "title": "Add Blood Bank",
            "encoding": "json",
            "method": "POST",
            "schema": self._blood_bank_schema()
        }
    def add_control_add_blood_donor(self):
        """
        This adds the add-blood-donors control to an object.  
        """
        self["@controls"]["bloodalert:add-message"] = {
            "href": api.url_for(BloodDonors),
            "title": "Add Blood Bank",
            "encoding": "json",
            "method": "POST",
            "schema": self._blood_donor_schema()
        }

    def add_control_add_blood_type(self):
        """
        This adds the add-blood-type control to an object. Intended ffor the 
        document object. Instead of adding a schema dictionary we are pointing
        to a schema url instead for two reasons: 1) to demonstrate both options;
        2) the user schema is relatively large.
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
            "schema": self._blood_type_schema(edit=True)
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
            "href": api.url_for(Blooddonor, donorId=donorId),
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
    """
class BloodDonor(Resource):
    """
    """
class BloodDonorHistoryList(Resource):
    """
    """
class BloodDonorHistory(Resource):
    """
    """

class BloodTypes(Resource):
    """
    """
class BloodType(Resource):
    """
    """



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
api.add_resource(BloodDonor, "/bloodalert/bloodtypes/<regex('btype-\d+'):bloodTypeId>/",
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
