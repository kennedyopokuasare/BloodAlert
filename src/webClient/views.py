"""
Routes and views for the flask application.
from . import resources
import src.resources as restful_api
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../../..'))

from datetime import datetime
from flask import render_template,Flask, request
#from src.bloodalert import bloodAlertResourcesApp
#from src.bloodalert import bloodAlertResourceAPI
import src.resources as resources
import json



app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():

    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )
@app.route('/register', methods=['GET','POST'])
def register():
    """Renders the register page"""
    if request.method=="GET":
         return render_template(
            'register.html',
            title='Donor Registration',
            year=datetime.now().year,
        )
    if request.method=="POST":
        """Do something"""
    

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/profile/')
@app.route('/profile')
def profile():
    """Renders the profile page."""
    return render_template(
        'profile.html',
        title='Profile',
        year=datetime.now().year,
        message='User profile page.'
    )

@app.route('/history/')
@app.route('/history')
def history():
    """Renders the history page."""
    return render_template(
        'history.html',
        title='History',
        year=datetime.now().year,
        message='User history page.'
    )

@app.route('/donate/')
@app.route('/donate')
def donate():
    """Renders the donate page."""
    return render_template(
        'donate.html',
        title='donate',
        year=datetime.now().year,
        message='User donate page.'
    )


@app.route('/profileEdit/')
@app.route('/profileEdit')
def profileEdit():
    """Renders the profileEdit page."""
    return render_template(
        'profileEdit.html',
        title='Edit Profile',
        year=datetime.now().year,
        message='Edit profile page.'
    )


if __name__ == "__main__":
    #resources.database.DEFAULT_DB_PATH="../db/bloodAlert.db"
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
