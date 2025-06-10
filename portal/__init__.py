# portal/__init__.py

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import json
from datetime import date
import time

# Cria as instâncias das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    """Cria e configura a instância principal da aplicação Flask."""
    app = Flask(__name__)

    # --- Carrega a configuração customizável do JSON ---
    config_path = os.path.join(app.root_path, '..', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            app.config['PORTAL_CONFIG'] = json.load(f)
    except FileNotFoundError:
        app.config['PORTAL_CONFIG'] = {
            "nome_empresa": "Portal Genérico",
            "imagem_fundo_login": "",
            "cores": {"primaria": "#4A2582", "texto_cabecalho": "#ffffff", "hover_botao": "#5e33a1"}
        }

    # --- Configurações da Aplicação ---
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/meu_portal_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'icons'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)

    # --- Inicialização das Extensões com a App ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # --- Filtros Customizados para os Templates ---
    @app.template_filter('format_date_br')
    def format_date_br(value):
        """Formata uma data para o padrão brasileiro (DD/MM/AAAA)."""
        if isinstance(value, date):
            return value.strftime('%d/%m/%Y')
        return value

    # --- Processador de Contexto para Cache Busting ---
    @app.context_processor
    def inject_version():
        """ Injeta a variável 'version' em todos os templates. """
        return {'version': int(time.time())}

    # --- NOVO PROCESSADOR DE CONTEXTO PARA CONFIGURAÇÕES GLOBAIS ---
    @app.context_processor
    def inject_portal_config():
        """Injeta a variável 'config' em todos os templates."""
        # Retorna um dicionário. A chave ('config') será o nome da variável no template.
        # O valor é o dicionário de configurações que carregamos do JSON.
        return {'config': current_app.config.get('PORTAL_CONFIG', {})}
    # ----------------------------------------------------------------

    # --- Registro de Blueprints (Rotas) ---
    from . import routes
    app.register_blueprint(routes.bp)

    return app