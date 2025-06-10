# portal/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from .models import User

class LoginForm(FlaskForm):
    """Formulário de Login para usuários existentes."""
    username = StringField('Nome de Usuário', validators=[DataRequired(message='O nome de usuário é obrigatório.')])
    password = PasswordField('Senha', validators=[DataRequired(message='A senha é obrigatória.')])
    remember_me = BooleanField('Lembrar-me') # Campo opcional para "lembrar-me"
    submit = SubmitField('Entrar')

class RegistrationForm(FlaskForm):
    """Formulário de Registro para novos usuários."""
    username = StringField('Nome de Usuário', validators=[
        DataRequired(message='O nome de usuário é obrigatório.'),
        Length(min=4, max=80, message='O nome de usuário deve ter entre 4 e 80 caracteres.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='O email é obrigatório.'),
        Email(message='Email inválido.')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='A senha é obrigatória.'),
        Length(min=6, message='A senha deve ter pelo menos 6 caracteres.')
    ])
    password2 = PasswordField(
        'Repita a Senha', validators=[
            DataRequired(message='Confirmação de senha é obrigatória.'),
            EqualTo('password', message='As senhas devem ser iguais.')
        ]
    )
    submit = SubmitField('Registrar')

    # Validadores personalizados (WTForms vai chamá-los automaticamente)
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Por favor, use outro ou faça login.')