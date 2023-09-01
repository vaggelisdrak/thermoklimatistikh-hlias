from . import db
from . import app
from itsdangerous import Serializer, SignatureExpired
#from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime,timedelta


class Users_database(db.Model, UserMixin):
    __tablename__ = 'Users_database'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), unique=True ,nullable=False)
    email = db.Column(db.String(200), unique=True ,nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    douleies = db.Column(db.String(20))

    #password encyption
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    

    def __init__(self, user, email, password_hash, douleies):
        self.user = user
        self.email = email
        self.password_hash = password_hash
        self.douleies = douleies

class MAIN_database(db.Model):
    __tablename__ = 'MAIN_database'
    __searchable__ =['date','visit_date','first_last_name','phone_number','address','device','model','problem_description']
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20) ,nullable=False)
    visit_date = db.Column(db.String(20),nullable=False)
    first_last_name = db.Column(db.String(200),nullable=False)
    phone_number = db.Column(db.String(200), unique=True ,nullable=False)
    address = db.Column(db.String(200), unique=True ,nullable=False)
    device = db.Column(db.String(200))
    model = db.Column(db.String(200))
    serial_number = db.Column(db.String(200))
    guarantee = db.Column(db.String(200))
    receipt = db.Column(db.String(200))
    spare = db.Column(db.String(200))
    order_number = db.Column(db.String(200))
    order_date = db.Column(db.String(20))
    model_code = db.Column(db.String(200))
    model_description = db.Column(db.String(200))
    quantity = db.Column(db.Integer)
    filename = db.Column(db.String(50),nullable=True)
    data = db.Column(db.LargeBinary,nullable=True)
    problem_description = db.Column(db.String(200))
    

    def __init__(self, date, visit_date, first_last_name, phone_number, address, device, model, serial_number, guarantee, 
    receipt,spare,order_number,order_date,model_code,model_description,quantity,filename,data,problem_description):
        self.date = date
        self.visit_date = visit_date
        self.first_last_name = first_last_name
        self.phone_number = phone_number
        self.address = address
        self.device = device
        self.model = model
        self.serial_number = serial_number
        self.guarantee = guarantee
        self.receipt = receipt
        self.spare = spare
        self.order_number = order_number
        self.order_date = order_date
        self.model_code = model_code
        self.model_description = model_description
        self.quantity = quantity
        self.filename = filename
        self.data = data
        self.problem_description = problem_description

class Files_database(db.Model):
    __tablename__ = 'Files_database'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    data = db.Column(db.LargeBinary)
    status = db.Column(db.String(50))

    def __init__(self, filename, data,status):
        self.filename = filename
        self.data = data
        self.status = status