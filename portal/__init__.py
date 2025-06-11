# portal/__init__.py

from flask import Flask, current_app, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import json
from datetime import date
import time
from dotenv import load_dotenv
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv() 

# Cria as instâncias das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cache = Cache()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    """Cria e configura a instância principal da aplicação Flask."""
    app = Flask(__name__)

    # --- Configurações da Aplicação ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'uma_chave_secreta_muito_segura_e_aleatoria_fallback'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://root:@localhost/meu_portal_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'svg'}
    app.config['ITEMS_PER_PAGE'] = 10 

    # Configurações do Flask-Caching
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

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

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'icons'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)

    if not app.debug and not app.testing:
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'portal_app.log'),
            maxBytes=1024 * 1024 * 10,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)

        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

        app.logger.info('Portal de Aplicações iniciado')

    @app.template_filter('format_date_br')
    def format_date_br(value):
        if isinstance(value, date):
            return value.strftime('%d/%m/%Y')
        return value

    @app.context_processor
    def inject_version():
        return {'version': int(time.time())}

    @app.context_processor
    def inject_portal_config():
        return {'config': current_app.config.get('PORTAL_CONFIG', {})}

    from . import routes
    app.register_blueprint(routes.bp)

    # NOVO: Importa e registra o Blueprint principal do admin
    from .admin import admin_bp 
    app.register_blueprint(admin_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app