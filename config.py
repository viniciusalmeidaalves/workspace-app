# config.py

import os

# Configurações de Banco de Dados
SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Chave Secreta para segurança do Flask
SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_muito_segura'

# Configurações de upload
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'portal', 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Configurações do Portal
PORTAL_CONFIG = {
    'APP_NAME': 'Meu Portal Interno',
    'BACKGROUND_IMAGE': 'images/login_background.jpg' # <--- CORREÇÃO AQUI
}