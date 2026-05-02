from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#Inicialización de SQLAlchemy
db = SQLAlchemy(app)

@app.route('/crear-tablas')
def crear_tablas():
    # Este comando crea las tablas en la base de datos si no existen
    db.create_all()
    return "¡Tablas creadas exitosamente en MySQL!"

if __name__ == '__main__':
    app.run(debug=True)
