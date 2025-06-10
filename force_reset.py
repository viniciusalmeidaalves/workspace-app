from portal import create_app, db
from portal.models import User

def force_update_credentials():
    app = create_app() # Sem o argumento config_class

    with app.app_context():
        target_username = 'vinicius almeida alves'
        new_password = '123'

        user_to_update = User.query.filter_by(username=target_username).first()

        if user_to_update:
            print(f"Utilizador '{target_username}' encontrado. A redefinir a palavra-passe...")
            user_to_update.set_password(new_password)
            db.session.commit()
            
            print("="*40)
            print("Palavra-passe redefinida com sucesso!")
            print(f"Utilizador: '{user_to_update.username}'")
            print(f"Nova Palavra-passe: '{new_password}'")
            print("="*40)
            print("Pode agora tentar fazer o login com as novas credenciais.")

        else:
            print(f"ERRO: O utilizador '{target_username}' não foi encontrado no banco de dados.")
            print("Verifique se o nome de utilizador no phpMyAdmin corresponde exatamente.")

if __name__ == '__main__':
    force_update_credentials()