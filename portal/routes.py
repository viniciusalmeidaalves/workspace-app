# portal/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Application, UsefulLink, Document, Banner
from .forms import LoginForm, RegistrationForm
from . import db, cache # NOVO: Importa 'cache'
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
import requests
import json
from datetime import datetime, timedelta


bp = Blueprint('main', __name__)

# --- Decorador de Admin ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Helper para validação de upload de arquivo ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# --- Funções para integração com APIs externas (agora com Caching) ---

@cache.cached(timeout=3600) # NOVO: Cacheia esta função por 1 hora (3600 segundos)
def get_ipmet_weather(city_id='224'):
    """Busca a previsão do tempo do IPMet para uma cidade específica (simulado)."""
    current_app.logger.info("Buscando previsão do tempo (simulada) - Pode estar em cache após a primeira vez.") # Para ver no log quando busca de fato
    try:
        today = datetime.now()
        
        data = {
            "city": "Ibaté",
            "state": "SP",
            "forecast": [
                {"date": today.strftime("%Y-%m-%d"), "condition": "Ensolarado", "min_temp": 20, "max_temp": 32, "icon": "fas fa-sun"},
                {"date": (today + timedelta(days=1)).strftime("%Y-%m-%d"), "condition": "Parcialmente Nublado", "min_temp": 19, "max_temp": 29, "icon": "fas fa-cloud-sun"},
                {"date": (today + timedelta(days=2)).strftime("%Y-%m-%d"), "condition": "Chuvoso", "min_temp": 21, "max_temp": 26, "icon": "fas fa-cloud-showers-heavy"}
            ]
        }
        return data['forecast']
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar previsão do tempo (simulado): {e}")
        return None

@cache.cached(timeout=3600) # NOVO: Cacheia esta função por 1 hora (3600 segundos)
def get_g1_news():
    """Simula a busca de notícias do G1."""
    current_app.logger.info("Buscando notícias G1 (simuladas) - Pode estar em cache após a primeira vez.") # Para ver no log quando busca de fato
    try:
        news = [
            {"title": "Notícias sobre tecnologia e inovações em IA", "url": "https://www.g1.globo.com/tecnologia", "source": "G1"},
            {"title": "Mercado financeiro: Análise da taxa de juros", "url": "https://www.g1.globo.com/economia", "source": "G1"},
            {"title": "Campeonato Brasileiro: Destaques da rodada", "url": "https://www.g1.globo.com/esportes", "source": "G1"},
            {"title": "Política nacional: Novos debates no congresso", "url": "https://www.g1.globo.com/politica", "source": "G1"},
            {"title": "Saúde e bem-estar: Dicas para uma vida saudável", "url": "https://www.g1.globo.com/saude", "source": "G1"},
        ]
        return news
    except Exception as e:
        current_app.logger.error(f"Erro ao buscar notícias (simulado): {e}")
        return []

# --- Rotas de Autenticação e Usuário Comum ---

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/login', methods=['GET', 'POST'])
def login():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    
    return render_template('login.html', title='Login', config=portal_config, form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    applications = current_user.applications if not current_user.is_admin else Application.query.all()
    return render_template('dashboard.html', title='Dashboard', config=portal_config, applications=applications)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota para usuários se registrarem publicamente."""
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, is_admin=False)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Conta criada com sucesso! Faça o login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Registrar', config=portal_config, form=form)

# --- ROTAS DA INTRANET ---
@bp.route('/intranet')
@login_required
def intranet():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    useful_links = UsefulLink.query.order_by(UsefulLink.category, UsefulLink.title).all()
    documents = Document.query.order_by(Document.category, Document.title).all()
    banners = Banner.query.order_by(Banner.order, Banner.id).all()
    
    links_by_category = {}
    for link in useful_links:
        links_by_category.setdefault(link.category, []).append(link)
    
    docs_by_category = {}
    for doc in documents:
        docs_by_category.setdefault(doc.category, []).append(doc)

    weather_forecast = get_ipmet_weather()
    g1_news = get_g1_news()
    
    now = datetime.now() 

    return render_template('intranet.html', 
                           title='Intranet', 
                           config=portal_config, 
                           links_uteis=useful_links,
                           links_by_category=links_by_category,
                           docs_by_category=docs_by_category,
                           weather_forecast=weather_forecast, 
                           g1_news=g1_news,
                           now=now,
                           banners=banners)


# Rota para servir arquivos PDF de forma segura
@bp.route('/documents/<filename>')
@login_required
def serve_document(filename):
    doc_path = os.path.join(current_app.root_path, 'static', 'uploads', 'documents')
    
    document_entry = Document.query.filter_by(filename=filename).first()
    if document_entry:
        try:
            return send_from_directory(doc_path, filename, as_attachment=False)
        except FileNotFoundError:
            flash('Documento não encontrado.', 'danger')
            return redirect(url_for('main.intranet'))
    else:
        flash('Acesso negado ou documento inválido.', 'danger')
        return redirect(url_for('main.intranet'))