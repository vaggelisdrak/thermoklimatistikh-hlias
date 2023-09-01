from flask import Flask, redirect, render_template, request, send_file, session, flash, jsonify, Response, url_for , Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null, true,desc
from flask_msearch import Search
from hashlib import *
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_login import *
import numpy as np
from flask_mail import Mail, Message, Attachment
from werkzeug.utils import secure_filename
import datetime
from requests import get
import json

db = SQLAlchemy(session_options={"autoflush": False})
app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.secret_key = 'hard-to-guess-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///USERS.db'
else:
    app.debug = False
    app.secret_key = os.environ.get('SECRET')
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://wklowuuajdnnnc:3ae368fbd56933d7d8d55ff72a6a5b7aca2864d5d8caad4fe44155b3f90488c3@ec2-54-80-122-11.compute-1.amazonaws.com:5432/dav6s6jdge1feq'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://oleqmlrqcmjyna:11e48ed048d5386c03cb8dc9146bb97fec610f345d6e1da05120c5bc9830e755@ec2-3-218-171-44.compute-1.amazonaws.com:5432/dica4lsvem1lp'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PIPENV_IGNORE_VIRTUALENVS']=True


def create_app():
    db.init_app(app)

    from .views import views
    from .admin import admin
    from .employees import employees

    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(employees, url_prefix = '/')
    app.register_blueprint(admin, url_prefix = '/')

    from .models import Users_database

    search = Search(app)
    search.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view ="login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users_database.query.get(int(user_id))
    
    return app

def create_database(app):
    db.create_all(app=app)
    print('Database created!')