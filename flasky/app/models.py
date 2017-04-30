#coding=utf-8

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from . import db
from . import login_manager


class Role(db.Model):
    """ 角色表 """

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        """ 对象显示字符串 """
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    """ 用户表 """

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False) 

    @property
    def password(self):
        """ 禁止读取密码 """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """   创建密码   """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """ 验证密码 """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """ 对象显示字符串 """
        return '<User %r>' % self.username

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False

        if data.get('confirm') != self.id:
            return False
            
        self.confirm = True
        db.session.add(self)
        return True

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    