# test_connection.py

from portal import create_app, db
<<<<<<< HEAD
from sqlalchemy import text
import sqlalchemy.exc

def check_database_connection():
    app = create_app() # Sem o argumento config_class
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
=======
from sqlalchemy import text # Importe a função 'text' para executar SQL puro
import sqlalchemy.exc # Importe as exceções do SQLAlchemy

def check_database_connection():
    """
    Cria o contexto da aplicação e tenta executar uma consulta simples
    para verificar a conexão com o banco de dados.
    """
    app = create_app()
    with app.app_context():
        try:
            # A forma mais simples de testar é executar um comando que não depende de nenhuma tabela.
            # 'SELECT 1' é o comando padrão para "pingar" um banco de dados.
            db.session.execute(text('SELECT 1'))
            
            # Se a linha acima não gerou um erro, a conexão está funcionando.
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
            print("="*50)
            print("✅ Conexão com o banco de dados bem-sucedida!")
            print(f"Conectado a: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("="*50)

        except sqlalchemy.exc.OperationalError as e:
<<<<<<< HEAD
=======
            # Este erro geralmente significa que o servidor não foi encontrado,
            # o nome do banco está errado, ou o usuário/senha estão incorretos.
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
            print("="*50)
            print("❌ Falha ao conectar ao banco de dados.")
            print("ERRO DE OPERAÇÃO: Verifique o nome do servidor, do banco, usuário e senha.")
            print(f"Detalhes: {e}")
            print("="*50)
        
        except Exception as e:
<<<<<<< HEAD
=======
            # Pega qualquer outro tipo de erro que possa ocorrer.
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
            print("="*50)
            print("❌ Ocorreu um erro inesperado ao tentar conectar.")
            print(f"Detalhes: {e}")
            print("="*50)

if __name__ == '__main__':
    check_database_connection()