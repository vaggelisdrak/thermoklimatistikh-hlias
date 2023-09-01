from flask import Flask, redirect, render_template, request, send_file, session, flash, jsonify, Response, url_for ,Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import *

views = Blueprint('views',__name__, template_folder='templates')

@views.route('/')
def index():
    return render_template('index.html')
