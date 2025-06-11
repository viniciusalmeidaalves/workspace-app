# portal/admin_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime # Importar datetime para parsear datas

from . import db
from .models import User, Application, UsefulLink, Document, Banner, Event # NOVO: Importa Event
from .forms import EventForm # NOVO: Importa EventForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# As rotas de administração foram movidas para sub-blueprints em portal/admin/
# Portanto, as rotas que estavam aqui serão removidas para evitar duplicação e usar a nova estrutura modularizada.

# --- ROTAS DO PAINEL DE ADMINISTRAÇÃO (APENAS O DASHBOARD PRINCIPAL PERMANECE AQUI, OUTRAS ROTAS EM SUB-BLUEPRINTS) ---

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    return render_template('admin/admin_dashboard.html', title='Painel Admin', config=portal_config)

# REMOVIDO: manage_applications foi movido para portal/admin/applications.py
# REMOVIDO: delete_application foi movido para portal/admin/applications.py
# REMOVIDO: manage_users foi movido para portal/admin/users.py
# REMOVIDO: edit_user_permissions foi movido para portal/admin/users.py
# REMOVIDO: delete_user foi movido para portal/admin/users.py
# REMOVIDO: manage_events foi movido para portal/admin/events.py
# REMOVIDO: edit_event foi movido para portal/admin/events.py
# REMOVIDO: delete_event foi movido para portal/admin/events.py
# REMOVIDO: manage_intranet_links foi movido para portal/admin/intranet_content.py
# REMOVIDO: edit_intranet_link foi movido para portal/admin/intranet_content.py
# REMOVIDO: delete_intranet_link foi movido para portal/admin/intranet_content.py
# REMOVIDO: manage_intranet_documents foi movido para portal/admin/intranet_content.py
# REMOVIDO: edit_intranet_document foi movido para portal/admin/intranet_content.py
# REMOVIDO: delete_intranet_document foi movido para portal/admin/intranet_content.py
# REMOVIDO: manage_intranet_banners foi movido para portal/admin/intranet_content.py
# REMOVIDO: edit_intranet_banner foi movido para portal/admin/intranet_content.py
# REMOVIDO: delete_intranet_banner foi movido para portal/admin/intranet_content.py