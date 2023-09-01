from flask import *
from flask_login import *
from faulthandler import disable
from io import BytesIO
import datetime
from fileinput import filename
from .models import *
from . import db
from flask_mail import Message,Mail
from sqlalchemy import desc

admin = Blueprint('admin',__name__)

@admin.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')

@admin.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('user')

        if username == "admin":
            email = request.form.get('email')
            password = request.form.get('password')
            print(username,email,password)

            #check if username and email are unique

            #users = []
            u = Users_database.query.all()
            for g in u:
                #users.append((g.username,g.email))
                if g.user == username or username == "admin":
                    flash("This username isn't available!",'error')
                    return render_template('sign_up.html')
                if g.email == email:
                    flash("This email isn't available!",'error')
                    return render_template('sign_up.html')

            #add new user to the database
            
            password = generate_password_hash(password,"sha256")
            user = Users_database(user=username ,email=email,password_hash=password,douleies=None)
            db.session.add(user)
            db.session.commit()
            print("admin created")

        return render_template("index.html")

@admin.route('/dashboard')
@login_required
def dashboard():
    return redirect('/plhrofories')


@admin.route('/synergeio', methods=['POST','GET'])
@login_required
def synergeio():
    if request.method == 'POST':
        user = request.form.get('user')
        email = request.form.get('email')
        password = request.form.get('password')
        douleies = "None"
        print(user,password)
        try:
            password = generate_password_hash(password,"sha256")
            user = Users_database(user=user,email=email,password_hash=password,douleies=douleies)
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

@admin.route('/visit_link/<int:a>')
@login_required
def visit_link(a):
    f = MAIN_database.query.get_or_404(a)
    return render_template('update_table.html',m=f)

@admin.route('/update/<int:id>', methods=['POST','GET'])
@login_required
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

@admin.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Users_database.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/synergeio')

    except:
        return "<h1>ERROR 404</h1>"

@admin.route('/plhrofories', methods=['POST','GET'])
@login_required
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

@admin.route('/users', methods=['POST','GET'])
@login_required
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

@admin.route('/download/<string:filename>')
@login_required
def download(filename):
    upload = MAIN_database.query.filter_by(filename=filename).first()
    print(upload)
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)

@admin.route('/delete_history/<int:id>')
@login_required
def delete_history(id):
    del_form = MAIN_database.query.get_or_404(id)
    try:
        db.session.delete(del_form)
        db.session.commit()
        return redirect('/plhrofories')

    except:
        return "<h1>ERROR 404</h1>"

@admin.route('/select', methods=['POST','GET'])
@login_required
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

@admin.route('/pdf', methods=['POST','GET'])
@login_required
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

@admin.route('/download_pdf/<string:filename>')
@login_required
def download_pdf(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    print(upload)
    return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)

@admin.route('/make_public/<string:filename>')
@login_required
def make_public(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    upload.status = "public"
    db.session.commit()
    print(upload)
    return redirect('/pdf')

@admin.route('/make_private/<string:filename>')
@login_required
def make_private(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    upload.status = "private"
    db.session.commit()
    print(upload)
    return redirect('/pdf')

@admin.route('/del_pdf/<string:filename>')
@login_required
def del_pdf(filename):
    upload = Files_database.query.filter_by(filename=filename).first()
    db.session.delete(upload)
    db.session.commit()
    return redirect('/pdf')
