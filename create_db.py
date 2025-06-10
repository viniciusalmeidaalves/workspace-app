# create_db.py

from portal import create_app, db
from portal.models import User, Application, UsefulLink, Document, Banner

def setup_database():
    app = create_app() # Sem o argumento config_class

    with app.app_context():
        print("Iniciando configuração do banco de dados...")
        
        db.create_all()
        print("Tabelas criadas com sucesso.")

        if not User.query.filter_by(username='admin').first():
            print("Criando usuário 'admin'...")
            admin_user = User(
                username='admin', 
                email='admin@example.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print("Usuário 'admin' criado.")
        
        if Application.query.count() == 0:
            print("Adicionando aplicações iniciais...")
            aplicacoes = [
                Application(name='Excel', link='#', icon='fas fa-file-excel'),
                Application(name='Word', link='#', icon='fas fa-file-word'),
                Application(name='Sistema de Tickets', link='#', icon='fas fa-ticket-alt')
            ]
            db.session.add_all(aplicacoes)
            print("Aplicações iniciais adicionadas.")

        db.session.commit()
        print("Banco de dados configurado com sucesso!")

if __name__ == '__main__':
    setup_database()