from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
import os
import resources
import database 

bloodAlertResourcesApp=resources.app
#bloodAlertResourcesAPI=resources.api
#bloodAlertResources=resources

DB_PATH = os.path.abspath(os.path.dirname(__file__)+ "../db/bloodAlert.db")
ENGINE = database.Engine(DB_PATH)

bloodAlertResourcesApp.config.update({"Engine": ENGINE})

from webClient.views import app as client


application = DispatcherMiddleware(bloodAlertResourcesApp, {
    '/web': client
})

if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True,)