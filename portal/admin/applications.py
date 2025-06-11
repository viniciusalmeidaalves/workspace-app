# portal/admin/applications.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
import os
import uuid
from werkzeug.utils import secure_filename
from .. import db
from ..models import Application # Importa Application
from ..forms import ApplicationForm # Importa ApplicationForm
from .utils import admin_required, allowed_file # Importa decorador e helper do utils

bp = Blueprint('applications', __name__, url_prefix='/applications') # Sub-Blueprint para aplicações

@bp.route('/', methods=['GET', 'POST']) # /admin/applications
@login_required
@admin_required
def manage_applications():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    form = ApplicationForm() # Instancia o formulário para adição

    if form.validate_on_submit(): # Se o formulário de adição for submetido
        name = form.name.data
        link = form.link.data
        icon_class = form.icon_class.data
        icon_file = request.files.get('icon_file') # Pega o arquivo do request diretamente, pois o FileField não foi usado para este form específico de adição

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
                # Continue para renderizar o template com o formulário e erros
        elif icon_class:
            icon_to_save = icon_class
        
        # Só tenta adicionar se tiver nome, link e algum ícone
        if name and link and icon_to_save:
            new_app = Application(name=name, link=link, icon=icon_to_save)
            db.session.add(new_app)
            db.session.commit()
            flash('Aplicação cadastrada com sucesso!', 'success')
            return redirect(url_for('admin.applications.manage_applications'))
        else: # Se faltar algum campo essencial ou o upload falhou
            if not (name and link):
                 flash('Nome e Link da aplicação são obrigatórios.', 'danger')
            if not icon_to_save:
                flash('Um Ícone (classe ou arquivo) é obrigatório.', 'danger')
    elif request.method == 'POST': # Caso o formulário não valide por outros motivos que não o upload
        flash('Erro ao adicionar aplicação. Verifique os campos.', 'danger')


    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    if search_query:
        search_pattern = f"%{search_query}%"
        applications_pagination = Application.query.filter(
            Application.name.ilike(search_pattern)
        ).order_by(Application.name).paginate(
            page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
        )
    else:
        applications_pagination = Application.query.order_by(Application.name).paginate(
            page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
        )
    applications = applications_pagination.items 

    return render_template('admin/manage_applications.html', 
                           title='Gerenciar Aplicações', 
                           config=portal_config, 
                           applications=applications,
                           applications_pagination=applications_pagination, # Nome da variável corrigido
                           form=form) # Passa o formulário para o template


@bp.route('/edit/<int:app_id>', methods=['GET', 'POST']) # NOVO: Rota para edição de aplicação
@login_required
@admin_required
def edit_application(app_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    app = Application.query.get_or_404(app_id)
    form = ApplicationForm(obj=app) # Preenche o formulário com os dados da aplicação

    if form.validate_on_submit():
        app.name = form.name.data
        app.link = form.link.data
        icon_class = form.icon_class.data
        icon_file = request.files.get('icon_file') # Pega o arquivo do request diretamente

        if icon_file and icon_file.filename != '':
            if allowed_file(icon_file.filename):
                # Deleta o ícone antigo se for um arquivo
                if app.icon and app.icon.startswith('uploads/icons/'):
                    old_icon_path = os.path.join(current_app.root_path, 'static', app.icon)
                    if os.path.exists(old_icon_path):
                        os.remove(old_icon_path)

                filename = secure_filename(icon_file.filename)
                unique_filename = str(uuid.uuid4()) + "_" + filename
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'icons', unique_filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                icon_file.save(save_path)
                app.icon = f'uploads/icons/{unique_filename}'
                flash('Novo arquivo de ícone enviado.', 'info')
            else:
                flash('Tipo de arquivo não permitido para ícone!', 'danger')
                return redirect(url_for('admin.applications.edit_application', app_id=app.id))
        elif icon_class: # Se uma classe de ícone foi fornecida
            app.icon = icon_class
        elif not icon_class and not app.icon: # Se não há ícone e nenhum novo foi fornecido
            flash('Um ícone (classe ou arquivo) é obrigatório.', 'danger')
            # Não redirecione para permitir que os erros do formulário sejam exibidos
            return render_template('admin/edit_application.html', 
                                   title='Editar Aplicação', 
                                   config=portal_config, 
                                   form=form, 
                                   app=app)


        db.session.commit()
        flash('Aplicação atualizada com sucesso!', 'success')
        return redirect(url_for('admin.applications.manage_applications'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao atualizar aplicação. Verifique os campos.', 'danger')
    
    return render_template('admin/edit_application.html', 
                           title='Editar Aplicação', 
                           config=portal_config, 
                           form=form, 
                           app=app)


@bp.route('/delete/<int:app_id>', methods=['POST']) # /admin/applications/delete/<id>
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
    return redirect(url_for('admin.applications.manage_applications'))