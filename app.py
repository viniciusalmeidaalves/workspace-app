# app.py

from portal import create_app, db
from flask_migrate import Migrate
from portal.models import User, Application, UsefulLink, Document, Banner

app = create_app() # Sem o argumento config_class

# migrate = Migrate(app, db) # Se já inicializado no __init__, esta linha pode ser removida ou comentada.

if __name__ == '__main__':
    app.run(debug=True)