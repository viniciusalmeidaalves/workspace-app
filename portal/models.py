# portal/models.py

from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlalchemy as sa # NOVO: Importa sqlalchemy como sa

user_application_permissions = db.Table('user_application_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('application_id', db.Integer, db.ForeignKey('application.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
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
    def __repr__(F):
        return f'<Document {F.title}>'

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    image_path = db.Column(db.String(255), nullable=False)
    link_url = db.Column(db.String(255), nullable=True)
    order = db.Column(sa.Integer(), nullable=True) # Agora 'sa' estará definido!
    def __repr__(self):
        return f'<Banner {self.title or self.id}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=True)
    all_day = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Event {self.title} - {self.start_date}>'

    def to_fullcalendar_format(self):
        event_data = {
            'id': self.id,
            'title': self.title,
            'start': self.start_date.isoformat(),
            'allDay': self.all_day
        }
        if self.end_date:
            event_data['end'] = self.end_date.isoformat()
        if self.description:
            event_data['extendedProps'] = {'description': self.description}
        return event_data