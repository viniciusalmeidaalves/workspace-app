# portal/admin/events.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from datetime import datetime # Importar datetime para parsear datas

from .. import db
from ..models import Event # Importa Event
from ..forms import EventForm # Importa EventForm
from .utils import admin_required # Importa o decorador admin_required do utils

bp = Blueprint('events', __name__, url_prefix='/events') # Sub-Blueprint para eventos

@bp.route('/', methods=['GET', 'POST']) # /admin/events
@login_required
@admin_required
def manage_events():
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    form = EventForm()

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data if form.end_date.data else None
        
        if form.all_day.data:
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if end_date:
                end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        new_event = Event(
            title=form.title.data,
            start_date=start_date,
            end_date=end_date,
            description=form.description.data,
            all_day=form.all_day.data
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Evento adicionado com sucesso!', 'success')
        return redirect(url_for('admin.events.manage_events'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao adicionar evento. Verifique os campos.', 'danger')
    
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    if search_query:
        search_pattern = f"%{search_query}%"
        events_pagination = Event.query.filter(
            Event.title.ilike(search_pattern) | Event.description.ilike(search_pattern)
        ).order_by(Event.start_date.desc()).paginate(
            page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
        )
    else:
        events_pagination = Event.query.order_by(Event.start_date.desc()).paginate(
            page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False
        )
    events = events_pagination.items
    return render_template('admin/manage_events.html', 
                           title='Gerenciar Eventos', 
                           config=portal_config, 
                           form=form,
                           events=events,
                           events_pagination=events_pagination) # Nome da variável corrigido

@bp.route('/edit/<int:event_id>', methods=['GET', 'POST']) # /admin/events/edit/<id>
@login_required
@admin_required
def edit_event(event_id):
    portal_config = current_app.config.get('PORTAL_CONFIG', {})
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)

    if form.validate_on_submit():
        event.title = form.title.data
        event.start_date = form.start_date.data
        event.end_date = form.end_date.data if form.end_date.data else None
        event.description = form.description.data
        event.all_day = form.all_day.data

        if event.all_day:
            event.start_date = event.start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if event.end_date:
                # Para eventos de dia inteiro, FullCalendar espera que a data de fim seja o dia seguinte
                # ao último dia do evento, à meia-noite. Ex: evento de 1 dia (dia 10) end_date = dia 11 00:00.
                # Aqui, vamos apenas garantir que a hora seja 00:00 para consistência.
                event.end_date = event.end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        db.session.commit()
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('admin.events.manage_events'))
    elif request.method == 'POST': # Se o formulário não validar (erros)
        flash('Erro ao atualizar evento. Verifique os campos.', 'danger')
    
    return render_template('admin/edit_event.html', 
                           title='Editar Evento', 
                           config=portal_config, 
                           form=form, 
                           event=event)

@bp.route('/delete/<int:event_id>', methods=['POST']) # /admin/events/delete/<id>
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Evento deletado com sucesso!', 'success')
    return redirect(url_for('admin.events.manage_events'))