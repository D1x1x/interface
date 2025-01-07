from app import app
from model import db, User

# Открываем контекст приложения
with app.app_context():
    # Очищаем таблицу пользователей (если нужно)
    db.session.query(User).delete()

    # Добавим админа
    admin = User(username='admin', role='admin')
    admin.set_password('1234')  # Установите пароль для администратора
    db.session.add(admin)

    # Добавим обычного пользователя
    user = User(username='user', role='user')
    user.set_password('4321')  # Установите пароль для обычного пользователя
    db.session.add(user)

    # Зафиксируем изменения
    db.session.commit()
