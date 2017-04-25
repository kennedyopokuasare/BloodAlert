"""
Routes and views for the flask application.
from . import resources
import src.resources as restful_api
"""

from datetime import datetime
from flask import render_template,Flask, request



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

if __name__ == "__main__":
    #Debug true activates automatic code reloading and improved error messages
    app.run(debug=True)
