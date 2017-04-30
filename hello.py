#coding=utf-8

import os
from threading import Thread
from datetime import datetime

from flask import Flask
from flask import request
from flask import make_response
from flask import abort
from flask import redirect
from flask import render_template
from flask import redirect
from flask import session
from flask import url_for
from flask import flash

from flask_mail import Mail
from flask_mail import Message 
from flask_migrate import Migrate, MigrateCommand 
from flask_script import Shell
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap 
from flask_script import Manager


from forms import NameForm


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hahaha'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.263.net'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_ADMIN'] = "1070445109@qq.com"
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]' 
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'


#把命令行解析功能添加到hello.py程序中
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
mail = Mail(app)

migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


class Role(db.Model):

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True) 
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name 

class User(db.Model):
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     """根目录"""
#     name = None
#     form = NameForm()
#     if form.validate_on_submit():
#         name = form.name.data
#         form.name.data = ''
#     user_agent = request.headers.get('User-Agent')
#     #response = make_response()
#     response = make_response(render_template("index.html", form=form, name=name, current_time=datetime.utcnow()))
#     response.set_cookie('answer', '42')
#     return response


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     name = None
#     form = NameForm()
#     if form.validate_on_submit():
#         old_name = session.get('name')
#         if old_name is not None and old_name != form.name.data:
#             flash('Looks like you have changed your name!')
#             flash('Haha!')
#         session['name'] = form.name.data
#         return redirect(url_for('index'))
#     return render_template('index.html', form=form, name=session.get('name'), \
#         current_time=datetime.utcnow())

@app.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            if  app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', \
                    'mail/new_user', user=user)
        else:
            session['known'] = True
            flash('Haha !')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',    \
        form=form, name=session.get('name'), \
        current_time=datetime.utcnow())

@app.route('/user/<name>')
def user(name):
    """用户名"""
    users = name
    if not users:
        abort(404)
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg) 

def send_email(to, subject, template, **kwargs):
    
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, \
        sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    th = Thread(target=send_async_email, args=[app, msg])
    th.start()
    return th

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
