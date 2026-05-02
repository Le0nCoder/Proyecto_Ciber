from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# --- BASE DE DATOS TEMPORAL DE USUARIOS ---
# En la fase final del proyecto, esta información se consultará en MySQL/PostgreSQL.
USERS_DB = {
    "dr_flores": {
        "id": 1,
        "username": "dr_flores",
        "password_hash": generate_password_hash("password_medico123"),
        "role": "medico",
        "hora_inicio_laboral": 8,  # 8:00 AM
        "hora_fin_laboral": 20     # 8:00 PM
    },
    "admin_cruz": {
        "id": 2,
        "username": "admin_cruz",
        "password_hash": generate_password_hash("password_admin456"),
        "role": "administrador",
        "hora_inicio_laboral": 0,  # Acceso 24 horas
        "hora_fin_laboral": 24
    }
}

def validar_horario_abac(usuario):
    """
    Componente del motor ABAC: Verifica si el usuario médico está accediendo 
    dentro de su horario laboral permitido.
    """
    hora_actual = datetime.now().hour
    
    # El administrador cuenta con acceso irrestricto por diseño
    if usuario['role'] == 'administrador':
        return True
        
    # Validar el rango de horas asignado para el rol médico
    if usuario['hora_inicio_laboral'] <= hora_actual < usuario['hora_fin_laboral']:
        return True
        
    return False


@app.route('/')
def index():
    """Página de inicio (Dashboard) protegida por sesión."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión con validación de credenciales y horario ABAC."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Por favor, complete todos los campos.', 'warning')
            return redirect(url_for('login'))

        # 1. Buscar al usuario en la estructura de datos
        user = USERS_DB.get(username)

        # 2. Validar usuario y hash de contraseña
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Credenciales incorrectas. Intente de nuevo.', 'danger')
            return redirect(url_for('login'))

        # 3. Validar el atributo de horario bajo el modelo ABAC
        if not validar_horario_abac(user):
            flash('Acceso denegado: Fuera del horario laboral permitido.', 'danger')
            return redirect(url_for('login'))

        # 4. Establecer la sesión una vez aprobadas las validaciones
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']

        flash('¡Inicio de sesión exitoso!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios con definición de atributos ABAC."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        hora_inicio = request.form.get('hora_inicio')
        hora_fin = request.form.get('hora_fin')

        # Validaciones de campos obligatorios
        if not username or not password or not role:
            flash('Por favor, llene todos los campos obligatorios.', 'warning')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'danger')
            return redirect(url_for('register'))

        # Evitar duplicados
        if username in USERS_DB:
            flash('El nombre de usuario o matrícula ya está registrado.', 'danger')
            return redirect(url_for('register'))

        # Convertir y validar los atributos de horario laboral para ABAC
        try:
            h_inicio = int(hora_inicio)
            h_fin = int(hora_fin)
            if not (0 <= h_inicio <= 23) or not (0 <= h_fin <= 24) or h_inicio >= h_fin:
                raise ValueError()
        except (ValueError, TypeError):
            flash('Rango de horario laboral inválido.', 'danger')
            return redirect(url_for('register'))

        # Guardar nuevo usuario con su contraseña hasheada de forma segura
        nuevo_id = len(USERS_DB) + 1
        USERS_DB[username] = {
            "id": nuevo_id,
            "username": username,
            "password_hash": generate_password_hash(password),
            "role": role,
            "hora_inicio_laboral": h_inicio,
            "hora_fin_laboral": h_fin
        }

        flash('Usuario registrado exitosamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/logout')
def logout():
    """Cierre de sesión seguro limpiando la cookie de sesión."""
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    try:
        # Intenta arrancar el servidor exclusivamente bajo HTTPS
        app.run(
            host='127.0.0.1',
            port=5000,
            ssl_context=('certs/server.crt', 'certs/server.key'),
            debug=True
        )
    except FileNotFoundError:
        print("[-] Error: No se encontraron los archivos de certificado.")
        print("[!] Asegúrese de que 'certs/server.crt' y 'certs/server.key' existan.")
        print("[!] Iniciando temporalmente en modo HTTP (No recomendado para producción).")
        
        # Fallback temporal para permitir el desarrollo
        app.run(host='127.0.0.1', port=5000, debug=True)