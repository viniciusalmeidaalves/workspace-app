# portal/__init__.py

<<<<<<< HEAD
from flask import Flask, current_app, render_template
=======
from flask import Flask, current_app
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import json
from datetime import date
import time
<<<<<<< HEAD
from dotenv import load_dotenv
from flask_caching import Cache
import logging # NOVO: Importa o módulo logging
from logging.handlers import RotatingFileHandler # NOVO: Para logs em arquivo com rotação

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv() 
=======
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62

# Cria as instâncias das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
<<<<<<< HEAD
cache = Cache()
=======
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    """Cria e configura a instância principal da aplicação Flask."""
    app = Flask(__name__)

<<<<<<< HEAD
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

=======
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
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

<<<<<<< HEAD
=======
    # --- Configurações da Aplicação ---
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/meu_portal_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'icons'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'documents'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'banners'), exist_ok=True)

<<<<<<< HEAD
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)

    # --- NOVO: Configuração de Logging ---
    if not app.debug and not app.testing: # Só configura logs em arquivo se não estiver em modo debug/teste
        log_dir = os.path.join(app.root_path, '..', 'logs')
        os.makedirs(log_dir, exist_ok=True) # Cria a pasta de logs se não existir

        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'portal_app.log'), # Caminho do arquivo de log
            maxBytes=1024 * 1024 * 10, # Tamanho máximo do arquivo de log (10 MB)
            backupCount=5 # Quantos arquivos de backup manter (portal_app.log.1, portal_app.log.2, etc.)
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO) # Define o nível mínimo de log para o arquivo

        app.logger.addHandler(file_handler) # Adiciona o handler de arquivo ao logger da aplicação
        app.logger.setLevel(logging.INFO) # Define o nível mínimo de log para o logger da aplicação

        app.logger.info('Portal de Aplicações iniciado')
    # ------------------------------------

    @app.template_filter('format_date_br')
    def format_date_br(value):
=======
    # --- Inicialização das Extensões com a App ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # --- Filtros Customizados para os Templates ---
    @app.template_filter('format_date_br')
    def format_date_br(value):
        """Formata uma data para o padrão brasileiro (DD/MM/AAAA)."""
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
        if isinstance(value, date):
            return value.strftime('%d/%m/%Y')
        return value

<<<<<<< HEAD
    @app.context_processor
    def inject_version():
        return {'version': int(time.time())}

    @app.context_processor
    def inject_portal_config():
        return {'config': current_app.config.get('PORTAL_CONFIG', {})}

    from . import routes
    app.register_blueprint(routes.bp)

    from . import admin_routes
    app.register_blueprint(admin_routes.admin_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

=======
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

>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
    return app