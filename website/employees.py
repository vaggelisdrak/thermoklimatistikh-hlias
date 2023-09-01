from flask import Flask, redirect, render_template, request, send_file, session, flash, jsonify, Response, url_for ,Blueprint, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from faulthandler import disable
from io import BytesIO
import datetime
from fileinput import filename
from .models import *
from . import db
from flask_mail import Message,Mail

employees = Blueprint('employees',__name__)

@employees.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('user')
        password = request.form.get('password')
        print(username,password)
        users = Users_database.query.all()

        for g in users:
            if g.user == username:
                user = Users_database.query.filter_by(user=username).first()
                if check_password_hash(user.password_hash, password):
                    login_user(user)
                    flash("You have successfully logged in",'success')
                    print(user.user)
                    username = user.user
                    print('logged in')

                    #session
                    session['name'] = username

                    if username == "admin":
                        return redirect(url_for('admin.dashboard'))
                    else:
                        return redirect('/douleies/'+str(username))
        else:
            error = 'The username or password is incorrect!'
            return render_template('index.html',error=error)
        
@employees.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect('/')

@app.route('/douleies/<string:user>')
@login_required
def douleies(user):
    douleiess = []
    l=0
    username = Users_database.query.filter_by(user=user).first()
    try:
        username.douleies =  list(dict.fromkeys(username.douleies.split(',')))
    except:
        pass
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
@login_required
def user_pdf():
    user = session.get('name')
    pdfs= Files_database.query.filter_by(status="public").all()
    return render_template('user_pdf.html',pdfs=pdfs,user=user)

@app.route('/edit/<int:id>' , methods=['POST','GET'])
@login_required
def edit(id):
    if request.method == "POST":
        m = MAIN_database.query.filter_by(id=id).first()
        print(m.filename)
        return render_template('update_table.html',m=m)

@app.route('/finish/<int:id>', methods=['POST','GET'])
@login_required
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
