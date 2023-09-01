from email import message
from faulthandler import disable
from io import BytesIO
from fileinput import filename
from flask import Flask, redirect, render_template, request, send_file, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null, true,desc
from flask_msearch import Search
from hashlib import *
from werkzeug.security import generate_password_hash, check_password_hash
import os
#from send_mail import send_mail

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

db = SQLAlchemy(app,session_options={"autoflush": False})
search = Search(app)
search.init_app(app)
search.create_index(update=True)
MSEARCH_INDEX_NAME =  os.path.join(app.root_path,'msearch')
MSEARCH_PRIMARY_KEY = 'id'
MSEARCH_ENABLE = True

class Users_database(db.Model):
    __tablename__ = 'Users_database'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), unique=True ,nullable=False)
    password = db.Column(db.String(200), nullable=False)
    douleies = db.Column(db.String(20))

    def __init__(self, user, password, douleies):
        self.user = user
        self.password = password
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

#homepage----------------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        print(user,password)

        users = []
        u = Users_database.query.all()
        for g in u:
            users.append((g.user,g.password))
        
        #print(users)
        for n,p in users:
            if (n==user and p==password):
                session['name'] = n
                if n=="admin":
                    return render_template('admin.html')
                else:
                    return redirect('/douleies/'+str(user))
        else:
            error = 'The username or password is incorrect!'
            return render_template('index.html',error=error)


#admin----------------------------------------------------------------------------------------

@app.route('/synergeio', methods=['POST','GET'])
def synergeio():
    if request.method == 'POST':
        user = request.form.get('user')
        password = request.form.get('password')
        douleies = "None"
        print(user,password)
        try:
            user = Users_database(user=user,password=password,douleies=douleies)
            db.session.add(user)
            db.session.commit()
        except:
            return "<h1>ERROR 404</h1>"
        return redirect('/synergeio')
    else:
        u = Users_database.query.all()
        for i in u[1:]:
            l=''
            #print(i.douleies.split(',')) 
            i.douleies =  list(dict.fromkeys(i.douleies.split(',')))
            print(i.douleies)

            #check if task exists
            for j in i.douleies:
                try:
                    t = MAIN_database.query.get_or_404(j)
                except:
                    i.douleies.remove(j)
            print(i.douleies)

            if len(i.douleies)>1:
                for j in i.douleies:
                    if j == str(i.douleies[-1]):
                        l+=j
                    else:
                        l+=j+','
            elif len(i.douleies)==1:
                l=i.douleies[0]
            else:
                l='None'
            print(l)
            i.douleies = l
            db.session.commit()
        return render_template('synergeio.html',users=u[1:])

@app.route('/visit_link/<int:a>')
def visit_link(a):
    f = MAIN_database.query.get_or_404(a)
    return render_template('update_table.html',m=f)

@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
    user_to_update = Users_database.query.get_or_404(id)
    print(user_to_update)
    if request.method == 'POST':
        user_to_update.user = request.form.get('user')
        user_to_update.password = request.form.get('password')
        user_to_update.douleies = request.form.get('jobs')
        try:
            db.session.commit()
            return redirect('/synergeio')
        except:
            return "<h1>ERROR 404</h1>"
    else:
        return render_template('update.html',user_to_update=user_to_update)

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users_database.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/synergeio')

    except:
        return "<h1>ERROR 404</h1>"

@app.route('/plhrofories', methods=['POST','GET'])
def plhrofories():
    if request.method == 'POST':
        search = request.form.get('search')
        '''m = MAIN_database.query.all()
        for i in m:
            if search in i.first_last_name() or i.address() or i.phone_number() or i.problem_description() or i.date():
                print(i.id)'''
        m = MAIN_database.query.msearch(search,fields=['date','visit_date','first_last_name','address','device','model','problem_description','phone_number']).all()
        l=0
        for i in m:
            l+=1
        u = Users_database.query.all()
        return render_template('plhrofories.html',m=m,u=u[1:],l=l,s=search)
    else:
        m = MAIN_database.query.order_by(desc('id')).all()
        u = Users_database.query.all()
        return render_template('plhrofories.html',m=m,u=u[1:])

@app.route('/users', methods=['POST','GET'])
def users():
    if request.method == 'POST':
        date = request.form.get('date')
        visit_date = request.form.get('visit_date')
        name = request.form.get('first_last_name')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        device = request.form.get('device')
        model = request.form.get('model')
        serial_number = request.form.get('serial_number')
        guarantee = request.form.get('guarantee')
        receipt = request.form.get('receipt')
        spare = request.form.get('spare')
        order_number = request.form.get('order_number')
        order_date = request.form.get('order_date')
        model_code = request.form.get('model_code')
        model_description = request.form.get('model_description')
        quantity = request.form.get('quantity')
        image = request.files.get('problem_image')
        problem_description = request.form.get('problem_description')
        print(date, visit_date,name , phone_number, address, device, model , serial_number, guarantee, 
        receipt,spare ,order_number,order_date ,model_code,model_description ,quantity,image,problem_description)

        user_to_update = MAIN_database.query.filter_by(address=address).first()
        if not user_to_update:
            user = MAIN_database(date=date, visit_date=visit_date, first_last_name = name, phone_number = phone_number , address = address, device = device, model = model, serial_number = serial_number, guarantee = guarantee, 
            receipt= receipt,spare = spare,order_number = order_number,order_date = order_date,model_code = model_code,model_description = model_description,quantity = quantity,filename=image.filename,data=image.read(),problem_description= problem_description)
            db.session.add(user)
            db.session.commit()
        else : #if record already exists->returns error
            user_to_update.date = date
            user_to_update.visit_date = visit_date
            user_to_update.first_last_name = name
            user_to_update.phone_number = phone_number
            user_to_update.address = address
            user_to_update.device = device
            user_to_update.model = model
            user_to_update.serial_number = serial_number
            user_to_update.guarantee = guarantee
            user_to_update.receipt = receipt
            user_to_update.spare = spare
            user_to_update.order_number = order_number
            user_to_update.order_date = order_date
            user_to_update.model_code = model_code
            user_to_update.model_description = model_description
            user_to_update.quantity = quantity
            if image:
                user_to_update.filename=image.filename
                user_to_update.data=image.read()
            user_to_update.problem_description = problem_description
            db.session.commit()
            user = session.get('name')
            return redirect('/douleies/'+str(user))

        message = 'Eπιτυχής υποβολή!'
        return render_template('forma.html',message=message)
    else:
        return render_template('forma.html')

@app.route('/download/<string:filename>')
def download(filename):
    upload = MAIN_database.query.filter_by(filename=filename).first()
    print(upload)
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)

@app.route('/delete_history/<int:id>')
def delete_history(id):
    del_form = MAIN_database.query.get_or_404(id)
    try:
        db.session.delete(del_form)
        db.session.commit()
        return redirect('/plhrofories')

    except:
        return "<h1>ERROR 404</h1>"

@app.route('/select', methods=['POST','GET'])
def select():
    if request.method == 'POST':
        couples=[]
        syn = request.form.get('synergeio')
        for i in syn.split(","):
            print(i,end="\n")
            i=i.replace('(','')
            i=i.replace(')','')
            i=i.replace("'",'')
            i=i.replace(" ",'')
            couples.append(i)
        print(couples)
        try:
            user_to_update = Users_database.query.filter_by(user=couples[0]).first()
            #if user_to_update.douleies:
                #return "<h1>ERROR - user unavailable!</h1>"  
            if user_to_update.douleies == "None":
                user_to_update.douleies = str(couples[1])
            else:
                user_to_update.douleies += (","+str(couples[1]))
            db.session.commit()
        except:
            return "<h1>ERROR 404</h1>"

        m = MAIN_database.query.order_by(desc('id')).all()
        u = Users_database.query.all()
        disable = 'True'
        return render_template('plhrofories.html',m=m,u=u[1:])
    else:
        return redirect('/plhrofories')

@app.route('/pdf', methods=['POST','GET'])
def pdf():
    if request.method == "POST":
        image = request.files.get('pdf_file')
        file_description = request.form.get('file_description')
        #try:
        file = Files_database(filename=image.filename,data=image.read(),status='')
        db.session.add(file)
        db.session.commit()
        #except:
            #return "<h1>ERROR 404</h1>"
        return redirect('/pdf')
    else:
        f = Files_database.query.all()
        return render_template('pdf.html',f=f)

@app.route('/download_pdf/<string:filename>')
def download_pdf(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    print(upload)
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)

@app.route('/make_public/<string:filename>')
def make_public(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    upload.status = "public"
    db.session.commit()
    print(upload)
    return redirect('/pdf')

@app.route('/make_private/<string:filename>')
def make_private(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    upload.status = "private"
    db.session.commit()
    print(upload)
    return redirect('/pdf')

@app.route('/del_pdf/<string:filename>')
def del_pdf(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    db.session.delete(upload)
    db.session.commit()
    return redirect('/pdf')

#synergeio--------------------------------------------------------------------------------

@app.route('/douleies/<string:user>')
def douleies(user):
    douleiess = []
    l=0
    username = Users_database.query.filter_by(user=user).first()
    username.douleies =  list(dict.fromkeys(username.douleies.split(',')))
    print(username.douleies)
    if username.douleies[0] == "None":
        l=0
    else:
        for i in username.douleies:
            m = MAIN_database.query.filter_by(id=int(i))
            douleiess.append(m)
            l+=1
    return render_template('douleies.html',m=douleiess,l=l)

@app.route('/user_pdf')
def user_pdf():
    user = session.get('name')
    pdfs= Files_database.query.filter_by(status="public").all()
    return render_template('user_pdf.html',pdfs=pdfs,user=user)

@app.route('/edit/<int:id>' , methods=['POST','GET'])
def edit(id):
    if request.method == "POST":
        m = MAIN_database.query.filter_by(id=id).first()
        print(m.filename)
        return render_template('update_table.html',m=m)

@app.route('/finish/<int:id>', methods=['POST','GET'])
def finish(id):
    if request.method == "POST":
        username = session.get('name')
        user = Users_database.query.filter_by(user=username).first()
        print(user.douleies)
        l=[]
        prev=''
        for i in user.douleies.split(','):
                l.append(i)
                l.append(',')
        l.pop()
        print(l)
        user.douleies = l
        print('-------------------------------------')
        '''for i in user.douleies:
            print(i)
        user.douleies = list(user.douleies)
        print(user.douleies)'''
        if len(user.douleies)==1:
            user.douleies.pop()
        else:
            #print(user.douleies[1])
            if str(id) == user.douleies[-1]:
                del(user.douleies[-2])
                del(user.douleies[-1])
            else:
                i=user.douleies.index(str(id))
                print(i)
                user.douleies.pop(i)
                user.douleies.pop(i)
        
        #user.douleies = user.douleies.replace(str(id),'')
        print('------------------------------------------')
        print(user.douleies)
        n=''
        if len(user.douleies) ==1:
            n+=str(user.douleies[0])
        elif len(user.douleies) ==0:
            n="None"
        else:
            for j in user.douleies:
                n+=str(j)  
        print(n)      
        user.douleies = n                                                                                                                            
        db.session.commit()
        print(user.douleies)
        return redirect('/douleies/'+str(user.user))

if __name__ == '__main__':
    #db.create_all()
    #user = Users_database(user="admin",password="x@6947022491k",douleies="None")
    #user = MAIN_database(date="19/2/22", visit_date="19/2/22", first_last_name = "antreas", phone_number = 6980087817 , address = "lasteiika", device = "malakia", model = "malakiaaa", serial_number = "561461a", guarantee = "yes", 
    #receipt= "yes",spare = "yes",order_number = "85496",order_date = "19/2/22",model_code = "25453",model_description = "ola kalaa",quantity = "5" ,problem_description= "mas gamhses")
    #db.session.add(user)
    #db.session.commit()
    app.run()