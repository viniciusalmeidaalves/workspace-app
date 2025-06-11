# portal/admin/__init__.py

from flask import Blueprint, render_template, current_app # Adicionado render_template, current_app
from flask_login import login_required # Adicionado login_required
from .utils import admin_required # Importa o decorador admin_required do utils

# Cria o Blueprint principal para o painel de administração
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Importa e registra os sub-blueprints aqui
from . import users
from . import applications
from . import intranet_content
from . import events

admin_bp.register_blueprint(users.bp)
admin_bp.register_blueprint(applications.bp)
admin_bp.register_blueprint(intranet_content.bp)
admin_bp.register_blueprint(events.bp)

# NOVO: Rota para o Dashboard principal do Admin (/)
@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    return render_template('admin/admin_dashboard.html', title='Painel Admin', config=portal_config)