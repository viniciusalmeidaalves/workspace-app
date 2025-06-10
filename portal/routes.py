# portal/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import User, Application, UsefulLink, Document, Banner # Adicionado Banner
from . import db
from functools import wraps
from flask import redirect, url_for, session, flash
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

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] != role:
                flash('Acesso não autorizado.', 'danger')
                return redirect(url_for('main.dashboard'))  # ajuste para sua rota principal
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Helper para validação de upload de arquivo ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# --- Funções para integração com APIs externas ---

def get_ipmet_weather(city_id='224'):
    """Busca a previsão do tempo do IPMet para uma cidade específica (simulado)."""
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

def get_g1_news():
    """Simula a busca de notícias do G1."""
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
        # AGORA REDIRECIONA PARA O DASHBOARD (Workspace)
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            # AGORA REDIRECIONA PARA O DASHBOARD (Workspace)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html', title='Login', config=portal_config)

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
        return redirect(url_for('main.dashboard')) # Se já logado, redireciona para dashboard
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Nome de usuário ou email já cadastrado.', 'warning')
        elif not username or not email or not password:
            flash('Todos os campos são obrigatórios.', 'danger')
        else:
            new_user = User(username=username, email=email, is_admin=False)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Conta criada com sucesso! Faça o login.', 'success')
            return redirect(url_for('main.login'))
    return render_template('register.html', title='Registrar', config=portal_config)

# --- ROTAS DA INTRANET ---
@bp.route('/intranet')
@login_required
def intranet():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    useful_links = UsefulLink.query.order_by(UsefulLink.category, UsefulLink.title).all()
    documents = Document.query.order_by(Document.category, Document.title).all()
    banners = Banner.query.order_by(Banner.order, Banner.id).all() # Buscar os banners
    
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
                           links_uteis=useful_links,  # Adicionado para a seção "Links Úteis"
                           links_by_category=links_by_category, # Mantido caso use em outro lugar
                           docs_by_category=docs_by_category,
                           weather_forecast=weather_forecast, 
                           g1_news=g1_news, # Adicionar vírgula aqui
                           now=now,
                           banners=banners) # Passar os banners para o template


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


# --- Rotas do Painel de Administração ---

@bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    return render_template('admin/admin_dashboard.html', title='Painel Admin', config=portal_config)

@bp.route('/admin/applications', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_applications():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if request.method == 'POST':
        name = request.form.get('name')
        link = request.form.get('link')
        icon_class = request.form.get('icon_class')
        icon_file = request.files.get('icon_file')
        icon_to_save = None
        if icon_file and icon_file.filename != '':
            if allowed_file(icon_file.filename):
                filename = secure_filename(icon_file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'icons', unique_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                icon_file.save(save_path)
                icon_to_save = f'uploads/icons/{unique_filename}'
            else:
                flash('Tipo de arquivo não permitido para ícone!', 'danger')
                return redirect(url_for('main.manage_applications'))
        elif icon_class:
            icon_to_save = icon_class
        
        if name and link and icon_to_save:
            new_app = Application(name=name, link=link, icon=icon_to_save)
            db.session.add(new_app)
            db.session.commit()
            flash('Aplicação cadastrada com sucesso!', 'success')
            return redirect(url_for('main.manage_applications'))
        else:
            flash('Nome, Link e um Ícone (classe ou arquivo) são obrigatórios.', 'danger')
    applications = Application.query.order_by(Application.name).all()
    return render_template('admin/manage_applications.html', title='Gerenciar Aplicações', config=portal_config, applications=applications)

@bp.route('/admin/applications/delete/<int:app_id>', methods=['POST'])
@login_required
@admin_required
def delete_application(app_id):
    app = Application.query.get_or_404(app_id)
    if app.icon and app.icon.startswith('uploads/icons/'):
        icon_path = os.path.join(current_app.root_path, 'static', app.icon)
        if os.path.exists(icon_path):
            os.remove(icon_path)
    db.session.delete(app)
    db.session.commit()
    flash('Aplicação deletada com sucesso!', 'success')
    return redirect(url_for('main.manage_applications'))

@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        if username and email and password:
            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash('Usuário ou email já existe.', 'warning')
            else:
                new_user = User(username=username, email=email, is_admin=is_admin)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('Usuário criado com sucesso!', 'success')
                return redirect(url_for('main.manage_users'))
        else:
            flash('Todos os campos são obrigatórios.', 'danger')
    users = User.query.order_by(User.username).all()
    return render_template('admin/manage_users.html', title='Gerenciar Usuários', config=portal_config, users=users)

@bp.route('/admin/user/<int:user_id>/permissions', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_permissions(user_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Não é possível alterar as permissões de um administrador.', 'warning')
        return redirect(url_for('main.manage_users'))
    if request.method == 'POST':
        assigned_apps_ids = request.form.getlist('applications', type=int)
        user.applications.clear()
        for app_id in assigned_apps_ids:
            app = Application.query.get(app_id)
            if app:
                user.applications.append(app)
        db.session.commit()
        flash(f'Permissões do usuário {user.username} atualizadas com sucesso!', 'success')
        return redirect(url_for('main.manage_users'))
    all_applications = Application.query.order_by(Application.name).all()
    return render_template('admin/edit_user_permissions.html', title='Editar Permissões', config=portal_config, user=user, applications=all_applications)

@bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Não é permitido deletar um usuário administrador.', 'danger')
        return redirect(url_for('main.manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('main.manage_users'))

# --- ROTAS DE ADMINISTRAÇÃO DA INTRANET ---

@bp.route('/admin/intranet/links', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_intranet_links():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        category = request.form.get('category', 'Geral')
        if title and url:
            new_link = UsefulLink(title=title, url=url, category=category)
            db.session.add(new_link)
            db.session.commit()
            flash('Link útil adicionado com sucesso!', 'success')
            return redirect(url_for('main.manage_intranet_links'))
        else:
            flash('Título e URL do link são obrigatórios.', 'danger')
    
    links = UsefulLink.query.order_by(UsefulLink.category, UsefulLink.title).all()
    return render_template('admin/manage_intranet_links.html', 
                           title='Gerenciar Links da Intranet', 
                           config=portal_config, 
                           links=links)

@bp.route('/admin/intranet/links/edit/<int:link_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intranet_link(link_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    link = UsefulLink.query.get_or_404(link_id)
    if request.method == 'POST':
        link.title = request.form.get('title')
        link.url = request.form.get('url')
        link.category = request.form.get('category', 'Geral')
        if link.title and link.url:
            db.session.commit()
            flash('Link útil atualizado com sucesso!', 'success')
            return redirect(url_for('main.manage_intranet_links'))
        else:
            flash('Título e URL do link são obrigatórios.', 'danger')
    return render_template('admin/edit_intranet_link.html', 
                           title='Editar Link da Intranet', 
                           config=portal_config, 
                           link=link)

@bp.route('/admin/intranet/links/delete/<int:link_id>', methods=['POST'])
@login_required
@admin_required
def delete_intranet_link(link_id):
    link = UsefulLink.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link útil deletado com sucesso!', 'success')
    return redirect(url_for('main.manage_intranet_links'))


@bp.route('/admin/intranet/documents', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_intranet_documents():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category', 'Documento')
        document_file = request.files.get('document_file')

        if not title or not document_file:
            flash('Título e arquivo do documento são obrigatórios.', 'danger')
        elif document_file and allowed_file(document_file.filename) and document_file.filename != '':
            filename = secure_filename(document_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', unique_filename) # Salvar em subpasta 'documents'
            os.makedirs(os.path.dirname(save_path), exist_ok=True) # Garante que a pasta existe
            document_file.save(save_path)
            
            new_document = Document(title=title, filename=unique_filename, category=category)
            db.session.add(new_document)
            db.session.commit()
            flash('Documento adicionado com sucesso!', 'success')
            return redirect(url_for('main.manage_intranet_documents'))
        else:
            flash('Tipo de arquivo não permitido para documento!', 'danger')
            
    documents = Document.query.order_by(Document.category, Document.title).all()
    return render_template('admin/manage_intranet_documents.html', 
                           title='Gerenciar Documentos da Intranet', 
                           config=portal_config, 
                           documents=documents)

@bp.route('/admin/intranet/documents/edit/<int:doc_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intranet_document(doc_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    doc = Document.query.get_or_404(doc_id)
    if request.method == 'POST':
        doc.title = request.form.get('title')
        doc.category = request.form.get('category', 'Documento')
        document_file = request.files.get('document_file')

        if not doc.title:
            flash('Título do documento é obrigatório.', 'danger')
        else:
            if document_file and document_file.filename != '':
                if allowed_file(document_file.filename):
                    # Deleta o arquivo antigo antes de salvar o novo
                    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', doc.filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                    filename = secure_filename(document_file.filename)
                    unique_filename = str(uuid.uuid4()) + "_" + filename
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', unique_filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    document_file.save(save_path)
                    doc.filename = unique_filename
                    flash('Novo arquivo de documento enviado.', 'info')
                else:
                    flash('Tipo de arquivo não permitido para documento!', 'danger')
                    return redirect(url_for('main.edit_intranet_document', doc_id=doc.id))

            db.session.commit()
            flash('Documento atualizado com sucesso!', 'success')
            return redirect(url_for('main.manage_intranet_documents'))
    return render_template('admin/edit_intranet_document.html', 
                           title='Editar Documento da Intranet', 
                           config=portal_config, 
                           doc=doc)


@bp.route('/admin/intranet/documents/delete/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def delete_intranet_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    # Deleta o arquivo físico antes de deletar a entrada do banco de dados
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('Arquivo físico deletado.', 'info')
    
    db.session.delete(doc)
    db.session.commit()
    flash('Documento deletado com sucesso!', 'success')
    return redirect(url_for('main.manage_intranet_documents'))


@bp.route('/admin/intranet/banners', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_intranet_banners():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    if request.method == 'POST':
        title = request.form.get('title')
        link_url = request.form.get('link_url') # URL para onde o banner redireciona
        order = request.form.get('order', type=int, default=0)
        banner_file = request.files.get('banner_file')

        if not banner_file or banner_file.filename == '':
            flash('Arquivo de imagem do banner é obrigatório.', 'danger')
        elif allowed_file(banner_file.filename):
            filename = secure_filename(banner_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            # Salvar em subpasta 'banners'
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True) # Garante que a pasta existe
            banner_file.save(save_path)
            image_path = f'uploads/banners/{unique_filename}' # Caminho relativo para o template
            
            new_banner = Banner(title=title, image_path=image_path, link_url=link_url, order=order)
            db.session.add(new_banner)
            db.session.commit()
            flash('Banner adicionado com sucesso!', 'success')
            return redirect(url_for('main.manage_intranet_banners'))
        else:
            flash('Tipo de arquivo não permitido para banner!', 'danger')
            
    banners = Banner.query.order_by(Banner.order, Banner.id).all()
    return render_template('admin/manage_intranet_banners.html', 
                           title='Gerenciar Banners da Intranet', 
                           config=portal_config, 
                           banners=banners)

@bp.route('/admin/intranet/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intranet_banner(banner_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    banner = Banner.query.get_or_404(banner_id)
    if request.method == 'POST':
        banner.title = request.form.get('title')
        banner.link_url = request.form.get('link_url')
        banner.order = request.form.get('order', type=int, default=0)
        banner_file = request.files.get('banner_file')

        if banner_file and banner_file.filename != '':
            if allowed_file(banner_file.filename):
                # Deleta o arquivo antigo antes de salvar o novo
                old_path = os.path.join(current_app.root_path, 'static', banner.image_path)
                if os.path.exists(old_path):
                    os.remove(old_path)

                filename = secure_filename(banner_file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', unique_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                banner_file.save(save_path)
                banner.image_path = f'uploads/banners/{unique_filename}'
                flash('Nova imagem de banner enviada.', 'info')
            else:
                flash('Tipo de arquivo não permitido para banner!', 'danger')
                return redirect(url_for('main.edit_intranet_banner', banner_id=banner.id))

        db.session.commit()
        flash('Banner atualizado com sucesso!', 'success')
        return redirect(url_for('main.manage_intranet_banners'))
    return render_template('admin/edit_intranet_banner.html', title='Editar Banner', config=portal_config, banner=banner)

@bp.route('/admin/intranet/banners/delete/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def delete_intranet_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    file_path = os.path.join(current_app.root_path, 'static', banner.image_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deletado com sucesso!', 'success')
    return redirect(url_for('main.manage_intranet_banners'))