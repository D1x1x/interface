from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from model import db, User, Client, Review, PaymentType, Room, Equipment, SportType, Subscription, Purchased, Trainer, \
    Schedule, Record
from config import Config
import logging
from datetime import datetime
from sqlalchemy.orm import joinedload

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

    tables = ['clients', 'reviews', 'purchased', 'rooms', 'equipment', 'sport_types', 'subscriptions', 'trainers',
              'schedule']
    return render_template('user_dashboard.html', tables=tables)


# Отображение таблицы
@app.route('/table/<table_name>', methods=['GET', 'POST'])
@login_required
def table_view(table_name):
    if current_user.role == 'user' and table_name not in ['clients', 'reviews', 'purchased', 'rooms', 'equipment',
                                                          'sport_types', 'subscriptions', 'trainers', 'schedule']:
        return redirect(url_for('user_dashboard'))

    # Обработка клиентов
    if table_name.lower() == 'clients':
        return handle_clients()
    elif table_name.lower() == 'reviews':
        return handle_reviews()
    elif table_name.lower() == 'payment_types':
        return handle_payment_types()
    elif table_name.lower() == 'rooms':
        return handle_rooms()
    elif table_name.lower() == 'equipment':
        return handle_equipment()
    elif table_name.lower() == 'sport_types':
        return handle_sport_types()
    elif table_name.lower() == 'subscriptions':
        return handle_subscriptions()
    elif table_name.lower() == 'purchased':
        return handle_purchased()
    elif table_name.lower() == 'trainers':
        return handle_trainers()
    elif table_name.lower() == 'schedule':
        return handle_schedule()
    elif table_name.lower() == 'records':
        return handle_records()

    # Если таблица не поддерживается
    flash(f'Table "{table_name}" is not supported.')
    return redirect(url_for('admin_dashboard' if current_user.role == 'admin' else 'user_dashboard'))


# --- Clients Routes ---
def handle_clients():
    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        new_client = Client(full_name=full_name, date_of_birth=date_of_birth, gender=gender, phone_number=phone_number)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('table_view', table_name='clients'))

    clients = Client.query.all()
    logger.debug(f'Clients fetched from DB: {clients}')
    return render_template('clients.html', clients=clients)


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
        return redirect(url_for('table_view', table_name='clients'))

    return render_template('edit_clients.html', client=client)


@app.route('/delete_client/<int:id_client>', methods=['POST'])
@login_required
def delete_client(id_client):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    client = Client.query.get_or_404(id_client)
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('table_view', table_name='clients'))


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
        return redirect(url_for('table_view', table_name='clients'))

    return render_template('add_client.html')


# --- Reviews Routes ---
def handle_reviews():
    if request.method == 'POST':
        comments = request.form['comments']
        rating = request.form['rating']
        id_client = request.form['id_client']
        date_of_review = request.form['date_of_review']

        new_review = Review(comments=comments, rating=rating, id_client=id_client, date_of_review=date_of_review)
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('table_view', table_name='reviews'))

    reviews = Review.query.all()
    for review in reviews:
        review.client = Client.query.get(review.id_client)

    return render_template('reviews.html', reviews=reviews, Client=Client)


@app.route('/edit_review/<int:id_reviews>', methods=['GET', 'POST'])
@login_required
def edit_reviews(id_reviews):
    reviews = Review.query.get_or_404(id_reviews)
    if request.method == 'POST':
        reviews.comments = request.form['comments']
        reviews.rating = request.form['rating']
        reviews.id_client = request.form['id_client']
        reviews.date_of_review = request.form['date_of_review']

        db.session.commit()
        return redirect(url_for('table_view', table_name='reviews'))

    return render_template('edit_reviews.html', reviews=reviews, Client=Client)


@app.route('/delete_review/<int:id_reviews>', methods=['POST'])
@login_required
def delete_review(id_reviews):
    reviews = Review.query.get_or_404(id_reviews)
    db.session.delete(reviews)
    db.session.commit()
    return redirect(url_for('table_view', table_name='reviews'))


@app.route('/add_review', methods=['GET', 'POST'])
@login_required
def add_review():
    if request.method == 'POST':
        comments = request.form['comments']
        rating = request.form['rating']
        id_client = request.form['id_client']
        date_of_review = request.form['date_of_review']
        new_review = Review(comments=comments, rating=rating, id_client=id_client, date_of_review=date_of_review)
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('table_view', table_name='reviews'))

    return render_template('add_review.html', Client=Client)

# --- Payment Types Routes ---
def handle_payment_types():
    if request.method == 'POST':
        name = request.form['name']
        new_payment_types = PaymentType(name=name)
        db.session.add(new_payment_types)
        db.session.commit()
        return redirect(url_for('table_view', table_name='payment_types'))

    payment_types = PaymentType.query.all()
    return render_template('payment_types.html', payment_types=payment_types, PaymentType=PaymentType)


@app.route('/edit_payment_type/<int:id_payment_types>', methods=['GET', 'POST'])
@login_required
def edit_payment_types(id_payment_types):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    payment_types = PaymentType.query.get_or_404(id_payment_types)
    if request.method == 'POST':
        payment_types.name = request.form['name']
        db.session.commit()
        return redirect(url_for('table_view', table_name='payment_types'))

    return render_template('edit_payment_types.html', payment_types=payment_types, PaymentType=PaymentType)


@app.route('/delete_payment_type/<int:id_payment_types>', methods=['POST'])
@login_required
def delete_payment_types(id_payment_types):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    payment_types = PaymentType.query.get_or_404(id_payment_types)
    db.session.delete(payment_types)
    db.session.commit()
    return redirect(url_for('table_view', table_name='payment_types'))


@app.route('/add_payment_types', methods=['GET', 'POST'])
@login_required
def add_payment_types():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        new_payment_types = PaymentType(name=name)
        db.session.add(new_payment_types)
        db.session.commit()
        return redirect(url_for('table_view', table_name='payment_types'))
    return render_template('add_payment_types.html', PaymentType=PaymentType)


# --- Rooms Routes ---
def handle_rooms():
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity']
        new_room = Room(name=name, capacity=capacity)
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully!')
        return redirect(url_for('table_view', table_name='rooms'))

    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms, Room=Room)


@app.route('/edit_room/<int:id_rooms>', methods=['GET', 'POST'])
@login_required
def edit_room(id_rooms):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    room = Room.query.get_or_404(id_rooms)
    if request.method == 'POST':
        room.name = request.form['name']
        room.capacity = request.form['capacity']
        db.session.commit()
        flash('Room updated successfully!')
        return redirect(url_for('table_view', table_name='rooms'))

    return render_template('edit_rooms.html', room=room, Room=Room)


@app.route('/delete_room/<int:id_rooms>', methods=['POST'])
@login_required
def delete_room(id_rooms):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    room = Room.query.get_or_404(id_rooms)
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully!')
    return redirect(url_for('table_view', table_name='rooms'))


@app.route('/add_room', methods=['GET', 'POST'])
@login_required
def add_room():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        capacity = request.form['capacity']
        new_room = Room(name=name, capacity=capacity)
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully!')
        return redirect(url_for('table_view', table_name='rooms'))
    return render_template('add_rooms.html', Room=Room)


# --- Equipment Routes ---
def handle_equipment():
    if request.method == 'POST':
        name = request.form['name']
        gym = request.form['gym']
        new_equipment = Equipment(name=name, gym=gym)
        db.session.add(new_equipment)
        db.session.commit()
        flash('Equipment added successfully!')
        return redirect(url_for('table_view', table_name='equipment'))
    equipment = Equipment.query.all()
    return render_template('equipment.html', equipment=equipment, Equipment=Equipment)


@app.route('/edit_equipment/<int:id_equipment>', methods=['GET', 'POST'])
@login_required
def edit_equipment(id_equipment):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    rooms = Room.query.all()  # Получаем список всех залов
    equipment = Equipment.query.get_or_404(id_equipment)

    if request.method == 'POST':
        equipment.name = request.form['name']
        equipment.id_rooms = request.form['gym']  # Обновляем id_rooms
        db.session.commit()
        flash('Equipment updated successfully!')
        return redirect(url_for('table_view', table_name='equipment'))

    return render_template('edit_equipment.html', equipment=equipment, rooms=rooms)



@app.route('/delete_equipment/<int:id_equipment>', methods=['POST'])
@login_required
def delete_equipment(id_equipment):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    equipment = Equipment.query.get_or_404(id_equipment)
    db.session.delete(equipment)
    db.session.commit()
    flash('Equipment deleted successfully!')
    return redirect(url_for('table_view', table_name='equipment'))


@app.route('/add_equipment', methods=['GET', 'POST'])
@login_required
def add_equipment():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    rooms = Room.query.all()  # Получаем список всех залов
    if request.method == 'POST':
        name = request.form['name']
        gym = request.form['gym']  # Используем правильный параметр 'gym'
        new_equipment = Equipment(name=name, id_rooms=gym)  # id_rooms, а не gym_id
        db.session.add(new_equipment)
        db.session.commit()
        flash('Equipment added successfully!')
        return redirect(url_for('table_view', table_name='equipment'))

    return render_template('add_equipment.html', rooms=rooms)




# --- Sport Types Routes ---
def handle_sport_types():
    if request.method == 'POST':
        name = request.form['name']
        new_sport_type = SportType(name=name)
        db.session.add(new_sport_type)
        db.session.commit()
        flash('Sport Type added successfully!')
        return redirect(url_for('table_view', table_name='sport_types'))

    sport_types = SportType.query.all()
    return render_template('sport_types.html', sport_types=sport_types, SportType=SportType)


@app.route('/edit_sport_type/<int:id_sport_types>', methods=['GET', 'POST'])
@login_required
def edit_sport_type(id_sport_types):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    sport_type = SportType.query.get_or_404(id_sport_types)
    if request.method == 'POST':
        sport_type.name = request.form['name']
        db.session.commit()
        flash('Sport Type updated successfully!')
        return redirect(url_for('table_view', table_name='sport_types'))
    return render_template('edit_sport_types.html', sport_type=sport_type, SportType=SportType)


@app.route('/delete_sport_type/<int:id_sport_types>', methods=['POST'])
@login_required
def delete_sport_type(id_sport_types):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    sport_type = SportType.query.get_or_404(id_sport_types)
    db.session.delete(sport_type)
    db.session.commit()
    flash('Sport Type deleted successfully!')
    return redirect(url_for('table_view', table_name='sport_types'))


@app.route('/add_sport_type', methods=['GET', 'POST'])
@login_required
def add_sport_type():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        new_sport_type = SportType(name=name)
        db.session.add(new_sport_type)
        db.session.commit()
        flash('Sport Type added successfully!')
        return redirect(url_for('table_view', table_name='sport_types'))
    return render_template('add_sport_types.html', SportType=SportType)


# --- Subscriptions Routes ---
def handle_subscriptions():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        new_subscription = Subscription(name=name, price=price)
        db.session.add(new_subscription)
        db.session.commit()
        flash('Subscription added successfully!')
        return redirect(url_for('table_view', table_name='subscriptions'))

    subscriptions = Subscription.query.all()
    return render_template('subscriptions.html', subscriptions=subscriptions, Subscription=Subscription)


@app.route('/edit_subscription/<int:id_subscriptions>', methods=['GET', 'POST'])
@login_required
def edit_subscription(id_subscriptions):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    subscription = Subscription.query.get_or_404(id_subscriptions)
    if request.method == 'POST':
        subscription.type_of_subscription = request.form['name']
        subscription.price = request.form['price']
        db.session.commit()
        flash('Subscription updated successfully!')
        return redirect(url_for('table_view', table_name='subscriptions'))
    return render_template('edit_subscriptions.html', subscription=subscription, Subscription=Subscription)


@app.route('/delete_subscription/<int:id_subscriptions>', methods=['POST'])
@login_required
def delete_subscription(id_subscriptions):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    subscription = Subscription.query.get_or_404(id_subscriptions)
    db.session.delete(subscription)
    db.session.commit()
    flash('Subscription deleted successfully!')
    return redirect(url_for('table_view', table_name='subscriptions'))


@app.route('/add_subscription', methods=['GET', 'POST'])
@login_required
def add_subscription():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        new_subscription = Subscription(type_of_subscription=name, price=price)
        db.session.add(new_subscription)
        db.session.commit()
        flash('Subscription added successfully!')
        return redirect(url_for('table_view', table_name='subscriptions'))
    return render_template('add_subscriptions.html', Subscription=Subscription)


# --- Purchased Routes ---
@app.route('/purchased')
@login_required
def handle_purchased():
    purchased = Purchased.query.all()
    for purchase in purchased:
        purchase.client = Client.query.get(purchase.id_client)
        purchase.subscription = Subscription.query.get(purchase.id_subscriptions)
        purchase.payment_type = PaymentType.query.get(purchase.id_payment_types)

    return render_template('purchased.html', purchased=purchased, Client=Client, Subscription=Subscription,
                           PaymentType=PaymentType)


@app.route('/edit_purchased/<int:id_purchased>', methods=['GET', 'POST'])
@login_required
def edit_purchased(id_purchased):
    purchased = Purchased.query.get_or_404(id_purchased)
    if request.method == 'POST':
        purchased.id_client = request.form['client_id']
        purchased.id_subscriptions = request.form['subscription_id']
        purchased.date_of_payment = request.form['purchase_date']
        purchased.id_payment_types = request.form['payment_type_id']
        purchased.date_of_subscription_start = request.form['date_of_subscription_start']
        purchased.date_of_subscription_end = request.form['date_of_subscription_end']

        db.session.commit()
        flash('Purchased updated successfully!')
        return redirect(url_for('table_view', table_name='purchased'))

    return render_template('edit_purchased.html', purchased=purchased, Client=Client, Subscription=Subscription,
                           PaymentType=PaymentType)


@app.route('/delete_purchased/<int:id_purchased>', methods=['POST'])
@login_required
def delete_purchased(id_purchased):
    purchased = Purchased.query.get_or_404(id_purchased)
    db.session.delete(purchased)
    db.session.commit()
    flash('Purchased deleted successfully!')
    return redirect(url_for('table_view', table_name='purchased'))


from datetime import datetime

@app.route('/add_purchased', methods=['GET', 'POST'])
@login_required
def add_purchased():
    if request.method == 'POST':
        # Получаем значения из формы
        client_id = request.form['client_id']
        subscription_id = request.form['subscription_id']
        payment_type_id = request.form['payment_type_id']
        purchase_date = request.form['purchase_date']
        date_of_subscription_start = request.form['date_of_subscription_start']
        date_of_subscription_end = request.form['date_of_subscription_end']



        # Создаем новый объект Purchased и сохраняем в базу
        new_purchased = Purchased(
            id_client=client_id,
            id_subscriptions=subscription_id,
            date_of_payment=purchase_date,
            id_payment_types=payment_type_id,
            date_of_subscription_start=date_of_subscription_start,
            date_of_subscription_end=date_of_subscription_end
        )

        db.session.add(new_purchased)
        db.session.commit()
        flash('Purchased added successfully!')
        return redirect(url_for('table_view', table_name='purchased'))

    return render_template('add_purchased.html', Client=Client, Subscription=Subscription, PaymentType=PaymentType)



# --- Trainers Routes ---
def handle_trainers():
    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        specialization = request.form['specialization']
        experience = request.form['experience']
        new_trainer = Trainer(full_name=full_name, date_of_birth=date_of_birth, specialization=specialization, experience=experience)
        db.session.add(new_trainer)
        db.session.commit()
        flash('Trainer added successfully!')
        return redirect(url_for('table_view', table_name='trainers'))
    trainers = Trainer.query.all()
    return render_template('trainers.html', trainers=trainers, Trainer=Trainer)


@app.route('/edit_trainer/<int:id_trainers>', methods=['GET', 'POST'])
@login_required
def edit_trainer(id_trainers):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    trainer = Trainer.query.get_or_404(id_trainers)
    if request.method == 'POST':
        trainer.full_name = request.form['full_name']
        trainer.date_of_birth = request.form['date_of_birth']
        trainer.specialization = request.form['specialization']
        trainer.experience = request.form['experience']
        db.session.commit()
        flash('Trainer updated successfully!')
        return redirect(url_for('table_view', table_name='trainers'))
    return render_template('edit_trainers.html', trainer=trainer, Trainer=Trainer)


@app.route('/delete_trainer/<int:id_trainers>', methods=['POST'])
@login_required
def delete_trainer(id_trainers):
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    trainer = Trainer.query.get_or_404(id_trainers)
    db.session.delete(trainer)
    db.session.commit()
    flash('Trainer deleted successfully!')
    return redirect(url_for('table_view', table_name='trainers'))


@app.route('/add_trainer', methods=['GET', 'POST'])
@login_required
def add_trainer():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        full_name = request.form['full_name']
        date_of_birth = request.form['date_of_birth']
        specialization = request.form['specialization']
        experience = request.form['experience']
        new_trainer = Trainer(full_name=full_name, date_of_birth=date_of_birth, specialization=specialization, experience=experience)
        db.session.add(new_trainer)
        db.session.commit()
        flash('Trainer added successfully!')
        return redirect(url_for('table_view', table_name='trainers'))
    return render_template('add_trainers.html', Trainer=Trainer)


@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def handle_schedule():
    if request.method == 'POST':
        room_id = request.form['room_id']
        trainer_id = request.form['trainer_id']
        sport_type_id = request.form['sport_type_id']
        day_of_week = request.form['day_of_week']  # День недели как строка
        time = request.form['time']

        new_schedule = Schedule(
            id_schedule=None,  # ID не передается, так как база данных сама сгенерирует его
            id_rooms=room_id,
            id_trainer=trainer_id,
            id_sport_types=sport_type_id,
            day_of_week=day_of_week,  # Сохраняем день недели
            time=time
        )
        db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule added successfully!')
        return redirect(url_for('handle_schedule'))

    schedule = Schedule.query.all()
    for schedul in schedule:
        schedul.room = Room.query.get(schedul.id_rooms)
        schedul.trainer = Trainer.query.get(schedul.id_trainer)
        schedul.sport_type = SportType.query.get(schedul.id_sport_types)

    return render_template('schedule.html', schedule=schedule, Room=Room, Trainer=Trainer, SportType=SportType)


@app.route('/edit_schedule/<int:id_schedule>', methods=['GET', 'POST'])
@login_required
def edit_schedule(id_schedule):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    schedule = Schedule.query.get_or_404(id_schedule)

    if request.method == 'POST':
        schedule.id_rooms = request.form['room_id']
        schedule.id_trainer = request.form['trainer_id']
        schedule.id_sport_types = request.form['sport_type_id']
        schedule.day_of_week = request.form['day_of_week']  # Обновляем день недели
        schedule.time = request.form['time']

        db.session.commit()
        flash('Schedule updated successfully!')
        return redirect(url_for('handle_schedule'))

    return render_template('edit_schedule.html', schedule=schedule, Room=Room, Trainer=Trainer, SportType=SportType)


@app.route('/delete_schedule/<int:id_schedule>', methods=['POST'])
@login_required
def delete_schedule(id_schedule):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    schedule = Schedule.query.get_or_404(id_schedule)
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully!')
    return redirect(url_for('handle_schedule'))


@app.route('/add_schedule', methods=['GET', 'POST'])
@login_required
def add_schedule():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        room_id = request.form['room_id']
        trainer_id = request.form['trainer_id']
        sport_type_id = request.form['sport_type_id']
        day_of_week = request.form['day_of_week']  # День недели
        time = request.form['time']  # Время

        new_schedule = Schedule(
            id_schedule=None,  # ID не передается, так как база данных сама сгенерирует его
            id_rooms=room_id,
            id_trainer=trainer_id,
            id_sport_types=sport_type_id,
            day_of_week=day_of_week,  # Сохраняем день недели
            time=time
        )
        db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule added successfully!')
        return redirect(url_for('handle_schedule'))  # Перенаправляем на страницу с расписанием

    return render_template('add_schedule.html', Room=Room, Trainer=Trainer, SportType=SportType)



@app.route('/records', methods=['GET', 'POST'])
@login_required
def handle_records():
    if request.method == 'POST':
        purchased_id = request.form['purchased_id']  # Используем purchased_id
        schedule_id = request.form['schedule_id']
        record_date = request.form['record_date']
        attendance = request.form['attendance']

        new_record = Record(
            id_purchased=purchased_id,  # Используем purchased_id
            id_schedule=schedule_id,
            date_of_record=record_date,
            attendance=attendance
        )

        db.session.add(new_record)
        db.session.commit()
        flash('Record added successfully!')
        return redirect(url_for('table_view', table_name='records'))

    # Получаем все записи
    records = Record.query.all()

    for record in records:
        record.purchased = Purchased.query.get(record.id_purchased)  # Получаем purchased для каждой записи
        record.schedule = Schedule.query.get(record.id_schedule)  # Получаем schedule для каждой записи

    return render_template('records.html', records=records, Purchased=Purchased, Schedule=Schedule)


@app.route('/edit_record/<int:id_records>', methods=['GET', 'POST'])
@login_required
def edit_record(id_records):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    record = Record.query.get_or_404(id_records)

    if request.method == 'POST':
        record.id_purchased = request.form['purchased_id']  # Обновляем purchased_id
        record.id_schedule = request.form['schedule_id']
        record.date_of_record = request.form['record_date']
        record.attendance = request.form['attendance']
        db.session.commit()
        flash('Record updated successfully!')
        return redirect(url_for('table_view', table_name='records'))

    return render_template('edit_record.html', record=record, Purchased=Purchased, Schedule=Schedule)


@app.route('/delete_record/<int:id_records>', methods=['POST'])
@login_required
def delete_record(id_records):
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    record = Record.query.get_or_404(id_records)
    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully!')
    return redirect(url_for('table_view', table_name='records'))


@app.route('/add_record', methods=['GET', 'POST'])
@login_required
def add_record():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    if request.method == 'POST':
        purchased_id = request.form['purchased_id']  # Используем purchased_id
        schedule_id = request.form['schedule_id']
        record_date = request.form['record_date']
        attendance = request.form['attendance']

        new_record = Record(
            id_purchased=purchased_id,  # Учитываем purchased
            id_schedule=schedule_id,
            date_of_record=record_date,
            attendance=attendance
        )
        db.session.add(new_record)
        db.session.commit()
        flash('Record added successfully!')
        return redirect(url_for('table_view', table_name='records'))

    return render_template('add_record.html', Purchased=Purchased, Schedule=Schedule)



# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
