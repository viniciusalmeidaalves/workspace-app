# portal/admin/intranet_content.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
import os
import uuid
from werkzeug.utils import secure_filename
from .. import db
from ..models import UsefulLink, Document, Banner # Importa os modelos
from ..forms import UsefulLinkForm, DocumentForm, BannerForm # NOVO: Importa os formulários
from .utils import admin_required, allowed_file # Importa decorador e helper do utils

bp = Blueprint('intranet_content', __name__, url_prefix='/intranet') # Sub-Blueprint para conteúdo da intranet

# --- Links Úteis ---
@bp.route('/links', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_intranet_links():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    form = UsefulLinkForm() # Instancia o formulário

    if form.validate_on_submit():
        new_link = UsefulLink(title=form.title.data, url=form.url.data, category=form.category.data)
        db.session.add(new_link)
        db.session.commit()
        flash('Link útil adicionado com sucesso!', 'success')
        return redirect(url_for('admin.intranet_content.manage_intranet_links'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao adicionar link útil. Verifique os campos.', 'danger')
        # Os erros serão exibidos pelo template através de form.errors

    page = request.args.get('page', 1, type=int)
    links_pagination = UsefulLink.query.order_by(UsefulLink.category, UsefulLink.title).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    links = links_pagination.items
    return render_template('admin/manage_intranet_links.html', 
                           title='Gerenciar Links da Intranet', 
                           config=portal_config, 
                           links=links,
                           pagination=links_pagination,
                           form=form) # Passa o formulário para o template

@bp.route('/links/edit/<int:link_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intranet_link(link_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    link = UsefulLink.query.get_or_404(link_id)
    form = UsefulLinkForm(obj=link) # Preenche o formulário com os dados existentes

    if form.validate_on_submit():
        link.title = form.title.data
        link.url = form.url.data
        link.category = form.category.data
        db.session.commit()
        flash('Link útil atualizado com sucesso!', 'success')
        return redirect(url_for('admin.intranet_content.manage_intranet_links'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao atualizar link útil. Verifique os campos.', 'danger')
    
    return render_template('admin/edit_intranet_link.html', 
                           title='Editar Link da Intranet', 
                           config=portal_config, 
                           link=link,
                           form=form) # Passa o formulário para o template

@bp.route('/links/delete/<int:link_id>', methods=['POST'])
@login_required
@admin_required
def delete_intranet_link(link_id):
    link = UsefulLink.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    flash('Link útil deletado com sucesso!', 'success')
    return redirect(url_for('admin.intranet_content.manage_intranet_links'))

# --- Documentos ---
@bp.route('/documents', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_intranet_documents():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    form = DocumentForm() # Instancia o formulário

    if form.validate_on_submit():
        title = form.title.data
        category = form.category.data
        document_file = form.document_file.data # Pega o arquivo do formulário WTForms

        if document_file: # Verifica se um arquivo foi enviado (o validador FileAllowed já tratou o tipo)
            filename = secure_filename(document_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            document_file.save(save_path)
            
            new_document = Document(title=title, filename=unique_filename, category=category)
            db.session.add(new_document)
            db.session.commit()
            flash('Documento adicionado com sucesso!', 'success')
            return redirect(url_for('admin.intranet_content.manage_intranet_documents'))
        else:
            flash('Arquivo do documento é obrigatório para um novo documento.', 'danger')
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao adicionar documento. Verifique os campos.', 'danger')
    
    page = request.args.get('page', 1, type=int)
    documents_pagination = Document.query.order_by(Document.category, Document.title).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    documents = documents_pagination.items
    return render_template('admin/manage_intranet_documents.html', 
                           title='Gerenciar Documentos da Intranet', 
                           config=portal_config, 
                           documents=documents,
                           pagination=documents_pagination,
                           form=form) # Passa o formulário para o template

@bp.route('/documents/edit/<int:doc_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intranet_document(doc_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    doc = Document.query.get_or_404(doc_id)
    form = DocumentForm(obj=doc) # Preenche o formulário com os dados existentes

    if form.validate_on_submit():
        doc.title = form.title.data
        doc.category = form.category.data
        document_file = form.document_file.data

        if document_file: # Se um novo arquivo foi enviado
            # Deleta o arquivo antigo se existir
            old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', doc.filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

            filename = secure_filename(document_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            document_file.save(save_path)
            doc.filename = unique_filename
            flash('Novo arquivo de documento enviado.', 'info')

        db.session.commit()
        flash('Documento atualizado com sucesso!', 'success')
        return redirect(url_for('admin.intranet_content.manage_intranet_documents'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao atualizar documento. Verifique os campos.', 'danger')

    return render_template('admin/edit_intranet_document.html', 
                           title='Editar Documento da Intranet', 
                           config=portal_config, 
                           doc=doc,
                           form=form) # Passa o formulário para o template

@bp.route('/documents/delete/<int:doc_id>', methods=['POST'])
@login_required
@admin_required
def delete_intranet_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash('Arquivo físico deletado.', 'info')
    
    db.session.delete(doc)
    db.session.commit()
    flash('Documento deletado com sucesso!', 'success')
    return redirect(url_for('admin.intranet_content.manage_intranet_documents'))

# --- Banners ---
@bp.route('/banners', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_intranet_banners():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    form = BannerForm() # Instancia o formulário

    if form.validate_on_submit():
        title = form.title.data
        link_url = form.link_url.data
        order = form.order.data
        banner_file = form.banner_file.data # Pega o arquivo do formulário WTForms

        if not banner_file: # Se for um novo banner, o arquivo é obrigatório
            flash('Arquivo de imagem do banner é obrigatório para um novo banner.', 'danger')
            return redirect(url_for('admin.intranet_content.manage_intranet_banners')) # Redireciona para exibir o flash
            
        filename = secure_filename(banner_file.filename)
        unique_filename = str(uuid.uuid4()) + "_" + filename
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', unique_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        banner_file.save(save_path)
        image_path = f'uploads/banners/{unique_filename}'
        
        new_banner = Banner(title=title, image_path=image_path, link_url=link_url, order=order)
        db.session.add(new_banner)
        db.session.commit()
        flash('Banner adicionado com sucesso!', 'success')
        return redirect(url_for('admin.intranet_content.manage_intranet_banners'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao adicionar banner. Verifique os campos.', 'danger')
    
    page = request.args.get('page', 1, type=int)
    banners_pagination = Banner.query.order_by(Banner.order, Banner.id).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
    )
    banners = banners_pagination.items
    return render_template('admin/manage_intranet_banners.html', 
                           title='Gerenciar Banners da Intranet', 
                           config=portal_config, 
                           banners=banners,
                           pagination=banners_pagination,
                           form=form) # Passa o formulário para o template

@bp.route('/banners/edit/<int:banner_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_intranet_banner(banner_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    banner = Banner.query.get_or_404(banner_id)
    form = BannerForm(obj=banner) # Preenche o formulário com os dados existentes

    if form.validate_on_submit():
        banner.title = form.title.data
        banner.link_url = form.link_url.data
        banner.order = form.order.data
        banner_file = form.banner_file.data # Pega o arquivo do formulário WTForms

        if banner_file: # Se um novo arquivo de banner foi enviado
            # Deleta o arquivo antigo se existir
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', os.path.basename(banner.image_path))
            if os.path.exists(old_path):
                os.remove(old_path)

            filename = secure_filename(banner_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', unique_filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            banner_file.save(save_path)
            banner.image_path = f'uploads/banners/{unique_filename}'
            flash('Nova imagem de banner enviada.', 'info')

        db.session.commit()
        flash('Banner atualizado com sucesso!', 'success')
        return redirect(url_for('admin.intranet_content.manage_intranet_banners'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao atualizar banner. Verifique os campos.', 'danger')

    return render_template('admin/edit_intranet_banner.html', 
                           title='Editar Banner', 
                           config=portal_config, 
                           banner=banner,
                           form=form) # Passa o formulário para o template

@bp.route('/banners/delete/<int:banner_id>', methods=['POST'])
@login_required
@admin_required
def delete_intranet_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners', os.path.basename(banner.image_path))
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner deletado com sucesso!', 'success')
    return redirect(url_for('admin.intranet_content.manage_intranet_banners'))