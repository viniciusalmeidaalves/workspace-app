# run.py
from portal import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=False) # Mude para False para testar o logging em arquivo