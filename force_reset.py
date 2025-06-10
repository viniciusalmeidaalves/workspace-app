from portal import create_app, db
from portal.models import User

def force_update_credentials():
<<<<<<< HEAD
    app = create_app() # Sem o argumento config_class

    with app.app_context():
        target_username = 'vinicius almeida alves'
        new_password = '123'

        user_to_update = User.query.filter_by(username=target_username).first()

        if user_to_update:
            print(f"Utilizador '{target_username}' encontrado. A redefinir a palavra-passe...")
            user_to_update.set_password(new_password)
=======
    """
    Encontra um utilizador pelo nome e redefine a sua palavra-passe de forma forçada.
    """
    app = create_app()

    with app.app_context():
        # --- Parâmetros da Atualização ---
        # Altere estes valores para o usuário e senha que desejar
        target_username = 'vinicius almeida alves'
        new_password = '123'
        # -----------------------------

        # 1. Procura o utilizador pelo nome atual no banco de dados.
        user_to_update = User.query.filter_by(username=target_username).first()

        # 2. Verifica se o utilizador foi encontrado
        if user_to_update:
            print(f"Utilizador '{target_username}' encontrado. A redefinir a palavra-passe...")
            
            # 3. Redefine a palavra-passe. O método 'set_password' cria
            #    o novo hash de forma segura.
            user_to_update.set_password(new_password)
            
            # 4. Salva (faz commit) das alterações no banco de dados
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
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