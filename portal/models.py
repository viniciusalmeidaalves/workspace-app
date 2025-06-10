# portal/models.py

<<<<<<< HEAD
from . import db
=======
<<<<<<< HEAD
from . import db
=======
from portal import db
>>>>>>> 0d0de7605e5a8e82167ee3b5ee539735fda73264
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

user_application_permissions = db.Table('user_application_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('application_id', db.Integer, db.ForeignKey('application.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    username = db.Column(db.String(80), unique=True, nullable=False)
=======
<<<<<<< HEAD
    username = db.Column(db.String(80), unique=True, nullable=False)
=======
    username = db.Column(db.String(150), unique=True, nullable=False)
>>>>>>> 0d0de7605e5a8e82167ee3b5ee539735fda73264
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    applications = db.relationship('Application', secondary=user_application_permissions, lazy='subquery', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.username}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    link = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(255), nullable=True)
    def __repr__(self):
        return f'<Application {self.name}>'

class UsefulLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), default='Geral', nullable=False)
    def __repr__(self):
        return f'<UsefulLink {self.title}>'

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    category = db.Column(db.String(50), default='Documento', nullable=False)
    def __repr__(self):
        return f'<Document {self.title}>'

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    image_path = db.Column(db.String(255), nullable=False)
    link_url = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    def __repr__(self):
        return f'<Banner {self.title or self.id}>'