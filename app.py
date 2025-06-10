# app.py

<<<<<<< HEAD
from portal import create_app, db
from flask_migrate import Migrate
from portal.models import User, Application, UsefulLink, Document, Banner

app = create_app() # Sem o argumento config_class

# migrate = Migrate(app, db) # Se já inicializado no __init__, esta linha pode ser removida ou comentada.

=======
from portal import create_app, db # Importa a função create_app e db do seu pacote portal
from flask_migrate import Migrate # Importe Migrate aqui também, embora já esteja no __init__
from portal.models import User, Application, UsefulLink, Document # Importe seus modelos para que o Flask-Migrate os veja

app = create_app()

# Configuração para o Flask-Migrate reconhecer o app e db
# Geralmente, se você já inicializou no __init__.py, não precisa inicializar novamente aqui.
# No entanto, para garantir que o Flask-Migrate encontre o contexto de app e db,
# é comum criar a instância Migrate no arquivo que Flask executa (este app.py)
# Se você já tem `migrate = Migrate()` e `migrate.init_app(app, db)` em portal/__init__.py,
# esta parte pode ser opcional ou usada para depuração.
# Para o seu caso, se o Flask-Migrate não está sendo encontrado, vamos garantir que ele seja instanciado aqui.
# migrate = Migrate(app, db) # Se já inicializado no __init__, esta linha pode ser removida ou comentada.


>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
if __name__ == '__main__':
    app.run(debug=True)