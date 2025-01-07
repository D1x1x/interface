from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, User, Client
from config import Config
import logging

# Настроим логирование
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

# Страница выхода
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Страница авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'user_dashboard'))
        else:
            flash('Неверный логин или пароль')

    return render_template('login.html')

# Панель администратора
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))

    tables = [
        'clients', 'reviews', 'payment_types', 'rooms', 'equipment',
        'sport_types', 'subscriptions', 'purchased', 'trainers', 'schedule', 'records'
    ]
    return render_template('admin_dashboard.html', tables=tables)

# Панель пользователя
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return redirect(url_for('admin_dashboard'))

    tables = ['clients', 'reviews', 'purchased']
    return render_template('user_dashboard.html', tables=tables)

# Отображение таблицы
@app.route('/table/<table_name>', methods=['GET', 'POST'])
@login_required
def table_view(table_name):
    if current_user.role == 'user' and table_name not in ['clients', 'reviews', 'purchased']:
        return redirect(url_for('user_dashboard'))

    if table_name.lower() == 'clients':
        if request.method == 'POST':  # Добавление нового клиента
            full_name = request.form['full_name']
            date_of_birth = request.form['date_of_birth']
            gender = request.form['gender']
            phone_number = request.form['phone_number']
            new_client = Client(full_name=full_name, date_of_birth=date_of_birth, gender=gender, phone_number=phone_number)
            db.session.add(new_client)
            db.session.commit()
            flash('Client added successfully!')
            return redirect(url_for('table_view', table_name='clients'))

        clients = Client.query.all()
        logger.debug(f'Clients fetched from DB: {clients}')  # Логирование полученных клиентов
        return render_template('clients.html', clients=clients)

    # Если таблица не поддерживается
    flash(f'Table "{table_name}" is not supported.')
    return redirect(url_for('admin_dashboard' if current_user.role == 'admin' else 'user_dashboard'))

# Редактирование клиента
@app.route('/edit_client/<int:id_client>', methods=['GET', 'POST'])
@login_required
def edit_client(id_client):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    client = Client.query.get_or_404(id_client)

    if request.method == 'POST':
        client.full_name = request.form['full_name']
        client.date_of_birth = request.form['date_of_birth']
        client.gender = request.form['gender']
        client.phone_number = request.form['phone_number']
        db.session.commit()
        flash('Client updated successfully!')
        return redirect(url_for('table_view', table_name='clients'))

    return render_template('edit_clients.html', client=client)

# Удаление клиента
@app.route('/delete_client/<int:id_client>', methods=['POST'])
@login_required
def delete_client(id_client):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    client = Client.query.get_or_404(id_client)
    db.session.delete(client)
    db.session.commit()
    flash('Client deleted successfully!')
    return redirect(url_for('table_view', table_name='clients'))

# Страница добавления клиента
@app.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        new_client = Client(full_name=full_name, date_of_birth=date_of_birth, gender=gender, phone_number=phone_number)
        db.session.add(new_client)
        db.session.commit()
        flash('Client added successfully!')
        return redirect(url_for('table_view', table_name='clients'))

    return render_template('add_client.html')

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
