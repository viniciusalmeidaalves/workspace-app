# test_connection.py

from portal import create_app, db
from sqlalchemy import text
import sqlalchemy.exc

def check_database_connection():
    app = create_app() # Sem o argumento config_class
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("="*50)
            print("✅ Conexão com o banco de dados bem-sucedida!")
            print(f"Conectado a: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("="*50)

        except sqlalchemy.exc.OperationalError as e:
            print("="*50)
            print("❌ Falha ao conectar ao banco de dados.")
            print("ERRO DE OPERAÇÃO: Verifique o nome do servidor, do banco, usuário e senha.")
            print(f"Detalhes: {e}")
            print("="*50)
        
        except Exception as e:
            print("="*50)
            print("❌ Ocorreu um erro inesperado ao tentar conectar.")
            print(f"Detalhes: {e}")
            print("="*50)

if __name__ == '__main__':
    check_database_connection()