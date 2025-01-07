from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Client(db.Model):
    __tablename__ = 'clients'

    id_client = db.Column(db.Integer, primary_key=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

    # Отношения
    reviews = db.relationship('Review', backref='client', lazy=True)
    purchased = db.relationship('Purchased', backref='client', lazy=True)

    def __repr__(self):
        return f"<Client {self.full_name}>"

# Таблица Отзывы
class Review(db.Model):
    __tablename__ = 'reviews'

    id_reviews = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.String(255), nullable=True)
    date_of_review = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<Review {self.id_reviews}>"

# Таблица Типы платежей
class PaymentType(db.Model):
    __tablename__ = 'payment_types'

    id_payment_types = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<PaymentType {self.name}>"

# Таблица Залы
class Room(db.Model):
    __tablename__ = 'rooms'

    id_rooms = db.Column(db.Integer, primary_key=True)
    capacity = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Отношения
    equipment = db.relationship('Equipment', backref='room', lazy=True)
    schedules = db.relationship('Schedule', backref='room', lazy=True)

    def __repr__(self):
        return f"<Room {self.name}>"

# Таблица Оборудование
class Equipment(db.Model):
    __tablename__ = 'equipment'

    id_equipment = db.Column(db.Integer, primary_key=True)
    id_rooms = db.Column(db.Integer, db.ForeignKey('rooms.id_rooms'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Equipment {self.name}>"

# Таблица Виды спорта
class SportType(db.Model):
    __tablename__ = 'sport_types'

    id_sport_types = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<SportType {self.name}>"

# Таблица Абонементы
class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id_subscriptions = db.Column(db.Integer, primary_key=True)
    type_of_subscription = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric, nullable=False)

    # Отношения
    purchased = db.relationship('Purchased', backref='subscription', lazy=True)

    def __repr__(self):
        return f"<Subscription {self.type_of_subscription}>"

# Таблица Покупки
class Purchased(db.Model):
    __tablename__ = 'purchased'

    id_purchased = db.Column(db.Integer, primary_key=True)
    id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'), nullable=False)
    id_subscriptions = db.Column(db.Integer, db.ForeignKey('subscriptions.id_subscriptions'), nullable=False)
    id_payment_types = db.Column(db.Integer, db.ForeignKey('payment_types.id_payment_types'), nullable=False)
    date_of_payment = db.Column(db.Date, nullable=False)
    date_of_subscription_start = db.Column(db.Date, nullable=False)
    date_of_subscription_end = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<Purchased {self.id_purchased}>"

# Таблица Тренеры
class Trainer(db.Model):
    __tablename__ = 'trainers'

    id_trainer = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    specialization = db.Column(db.String(255), nullable=False)

    # Отношения
    schedules = db.relationship('Schedule', backref='trainer', lazy=True)

    def __repr__(self):
        return f"<Trainer {self.full_name}>"

# Таблица Расписание
class Schedule(db.Model):
    __tablename__ = 'schedule'

    id_schedule = db.Column(db.Integer, primary_key=True)
    id_trainer = db.Column(db.Integer, db.ForeignKey('trainers.id_trainer'), nullable=False)
    id_rooms = db.Column(db.Integer, db.ForeignKey('rooms.id_rooms'), nullable=False)
    id_sport_types = db.Column(db.Integer, db.ForeignKey('sport_types.id_sport_types'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    time = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"<Schedule {self.day_of_week} {self.time}>"

# Таблица Записи на тренировки
class Record(db.Model):
    __tablename__ = 'records'

    id_records = db.Column(db.Integer, primary_key=True)
    id_purchased = db.Column(db.Integer, db.ForeignKey('purchased.id_purchased'), nullable=False)
    id_schedule = db.Column(db.Integer, db.ForeignKey('schedule.id_schedule'), nullable=False)
    date_of_record = db.Column(db.Date, nullable=False)
    attendance = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<Record {self.id_records}>"