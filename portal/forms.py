# portal/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateTimeLocalField, IntegerField # Importar IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional, URL # Importar URL
from flask_wtf.file import FileField, FileAllowed # NOVO: Importar para upload de arquivos
from .models import User, Event # Importar Event para o EventForm

class LoginForm(FlaskForm):
    """Formulário de Login para usuários existentes."""
    username = StringField('Nome de Usuário', validators=[DataRequired(message='O nome de usuário é obrigatório.')])
    password = PasswordField('Senha', validators=[DataRequired(message='A senha é obrigatória.')])
    remember_me = BooleanField('Lembrar-me')
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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado. Por favor, use outro ou faça login.')

class EventForm(FlaskForm):
    """Formulário para adicionar/editar eventos no calendário."""
    title = StringField('Título do Evento', validators=[DataRequired(message='O título é obrigatório.')])
    start_date = DateTimeLocalField('Data/Hora de Início', format='%Y-%m-%dT%H:%M', validators=[DataRequired(message='A data de início é obrigatória.')])
    end_date = DateTimeLocalField('Data/Hora de Fim (Opcional)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    description = TextAreaField('Descrição (Opcional)')
    all_day = BooleanField('Evento de Dia Inteiro')
    submit = SubmitField('Salvar Evento')

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('A data/hora de fim não pode ser anterior à data/hora de início.')

class ApplicationForm(FlaskForm):
    """Formulário para adicionar/editar aplicações."""
    name = StringField('Nome da Aplicação', validators=[DataRequired(message='O nome da aplicação é obrigatório.'), Length(max=100)])
    link = StringField('Link da Aplicação', validators=[DataRequired(message='O link da aplicação é obrigatório.'), Length(max=255), URL(message='Insira uma URL válida.')]) # Adicionado URL validator
    icon_class = StringField('Classe do Ícone (FontAwesome)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Salvar Aplicação')

# NOVO: Formulário para Links Úteis
class UsefulLinkForm(FlaskForm):
    title = StringField('Título do Link', validators=[DataRequired(message='O título é obrigatório.'), Length(max=150)])
    url = StringField('URL do Link', validators=[DataRequired(message='A URL é obrigatória.'), Length(max=255), URL(message='Insira uma URL válida.')])
    category = StringField('Categoria', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Salvar Link')

# NOVO: Formulário para Documentos
class DocumentForm(FlaskForm):
    title = StringField('Título do Documento', validators=[DataRequired(message='O título é obrigatório.'), Length(max=150)])
    category = StringField('Categoria', validators=[Optional(), Length(max=50)])
    document_file = FileField('Arquivo do Documento', validators=[
        Optional(),
        FileAllowed(['txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'], 'Apenas documentos (txt, pdf, doc, docx, xls, xlsx, ppt, pptx) são permitidos.')
    ])
    submit = SubmitField('Salvar Documento')

# NOVO: Formulário para Banners
class BannerForm(FlaskForm):
    title = StringField('Título (Opcional)', validators=[Optional(), Length(max=150)])
    link_url = StringField('URL do Link (Opcional)', validators=[Optional(), Length(max=255), URL(message='Insira uma URL válida se preenchido.')])
    order = IntegerField('Ordem de Exibição', validators=[DataRequired(message='A ordem é obrigatória.')])
    banner_file = FileField('Arquivo de Imagem do Banner', validators=[
        Optional(), # Será required na lógica da rota para adição
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'svg'], 'Apenas imagens (png, jpg, jpeg, gif, svg) são permitidas.')
    ])
    submit = SubmitField('Salvar Banner')