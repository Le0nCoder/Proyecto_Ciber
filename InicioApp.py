from flask import Flask, render_template, redirect, url_url, request, flash, session
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Por favor, complete todos los campos.','error')
            return redirect(url_for('login'))
        return render_template('login.html')

if __name__ == '__main__':
    try:
        app.run(
            host = '127.0.0.1',
            port = 5000,
            ssl_context = ('certs/server.crt','certs/server.key'),
            debug = True
        )
    except FileNotFoundError:
        print("[-] Error: No se encontraron los archivos de certificado. Asegúrese de que 'certs/server.crt' y 'certs/server.key' existan.")

        app.run(host = '127.0.0.1', port = 5000, debug = True)