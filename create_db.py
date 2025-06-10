# create_db.py

from portal import create_app, db
from portal.models import User, Application

def setup_database():
    """
    Função para criar tabelas e popular o banco de dados com dados iniciais.
    Execute este script apenas uma vez.
    """
    app = create_app()

    with app.app_context():
        print("Iniciando configuração do banco de dados...")
        
        # Cria todas as tabelas definidas nos models
        db.create_all()
        print("Tabelas criadas com sucesso.")

        # --- Adiciona dados iniciais ---
        
        # Cria o usuário administrador se ele não existir
        if not User.query.filter_by(username='admin').first():
            print("Criando usuário 'admin'...")
            admin_user = User(
                username='admin', 
                email='admin@example.com',
                is_admin=True  # Define este usuário como administrador
            )
            admin_user.set_password('admin123') # A senha será 'admin123'
            db.session.add(admin_user)
            print("Usuário 'admin' criado.")
        
        # Adiciona aplicações de exemplo se não houver nenhuma
        if Application.query.count() == 0:
            print("Adicionando aplicações iniciais...")
            aplicacoes = [
                Application(name='Excel', link='#', icon='fas fa-file-excel'),
                Application(name='Word', link='#', icon='fas fa-file-word'),
                Application(name='Sistema de Tickets', link='#', icon='fas fa-ticket-alt')
            ]
            db.session.add_all(aplicacoes)
            print("Aplicações iniciais adicionadas.")

        # Salva todas as alterações no banco de dados
        db.session.commit()
        print("Banco de dados configurado com sucesso!")

if __name__ == '__main__':
    setup_database()