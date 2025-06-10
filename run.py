# run.py
<<<<<<< HEAD
from portal import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=False) # Mude para False para testar o logging em arquivo
=======

from portal import create_app

# Cria a aplicação usando a factory function
app = create_app()

if __name__ == '__main__':
    # Roda a aplicação em modo de debug para facilitar o desenvolvimento
    app.run(debug=True)
>>>>>>> 89111cd5202a77305c75b47fa782be21cea0cd62
