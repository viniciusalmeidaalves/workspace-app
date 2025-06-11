# portal/admin/utils.py

from flask import flash, redirect, url_for, current_app
from flask_login import current_user
from functools import wraps
import os

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