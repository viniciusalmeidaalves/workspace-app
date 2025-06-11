# portal/admin/users.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from .. import db # Importa db do pacote portal
from ..models import User, Application # Importa User e Application
from ..forms import RegistrationForm # NOVO: Importa RegistrationForm
from .utils import admin_required # Importa o decorador admin_required do utils

bp = Blueprint('users', __name__, url_prefix='/users') # Sub-Blueprint para usuários

@bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    form = RegistrationForm() # Instancia o formulário para a seção de adição de usuário

    if form.validate_on_submit(): # Se o formulário de adição for submetido
        username = form.username.data
        email = form.email.data
        password = form.password.data
        is_admin = 'is_admin_new' in request.form # Note: o checkbox tem id 'is_admin_new' no HTML para evitar conflito

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Usuário ou email já existe.', 'warning')
        else:
            new_user = User(username=username, email=email, is_admin=is_admin)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('admin.users.manage_users'))
    
    page = request.args.get('page', 1, type=int)
    users_pagination = User.query.order_by(User.username).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    users = users_pagination.items
    return render_template('admin/manage_users.html', 
                           title='Gerenciar Usuários', 
                           config=portal_config, 
                           users=users,
                           pagination=users_pagination,
                           form=form) # Passa o formulário para o template

@bp.route('/<int:user_id>/permissions', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_permissions(user_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    user = User.query.get_or_404(user_id)
    # Não vamos usar um formulário WTForms para este, pois é um formulário simples de checkboxes.
    # No entanto, a lógica de desabilitar a alteração do próprio admin ainda é importante.

    if user.is_admin and not current_user.id == user.id: # Um admin não pode mudar as permissões de outro admin, exceto as suas próprias.
        flash('Não é possível alterar as permissões de um administrador.', 'warning')
        return redirect(url_for('admin.users.manage_users'))

    if request.method == 'POST':
        assigned_apps_ids = request.form.getlist('applications', type=int)
        
        # Lógica para checkbox 'is_admin'
        # Apenas permite alteração se o usuário não for admin, ou se for ele mesmo (para o caso de despromover a si mesmo, o que exige cuidado).
        # Para simplificar e evitar que um admin se bloqueie, a permissão de admin é desabilitada no template para administradores.
        # Portanto, esta lógica deve ser mais robusta se você quiser permitir que um admin remova sua própria permissão de admin.
        # Por enquanto, mantemos a permissão de administrador desabilitada para edição no template para administradores.
        
        # Limpar permissões existentes e adicionar as novas
        user.applications.clear()
        for app_id in assigned_apps_ids:
            app = Application.query.get(app_id)
            if app:
                user.applications.append(app)
        
        db.session.commit()
        flash(f'Permissões do usuário {user.username} atualizadas com sucesso!', 'success')
        return redirect(url_for('admin.users.manage_users'))
    
    all_applications = Application.query.order_by(Application.name).all()
    return render_template('admin/edit_user_permissions.html', 
                           title='Editar Permissões', 
                           config=portal_config, 
                           user=user, 
                           applications=all_applications)

@bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Não é permitido deletar um usuário administrador.', 'danger')
        return redirect(url_for('admin.users.manage_users'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('admin.users.manage_users'))