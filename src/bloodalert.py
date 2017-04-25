from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from resources import app as restful_api
from webClient.views import app as client

application = DispatcherMiddleware(restful_api, {
    '/web': client
})

if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True,)