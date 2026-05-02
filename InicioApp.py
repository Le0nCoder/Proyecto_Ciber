from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#Inicialización de SQLAlchemy
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)