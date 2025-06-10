# run.py

from portal import create_app

# Cria a aplicação usando a factory function
app = create_app()

if __name__ == '__main__':
    # Roda a aplicação em modo de debug para facilitar o desenvolvimento
    app.run(debug=True)