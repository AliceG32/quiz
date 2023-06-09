# Подключаем необходимы библиотеки
import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from data_db.db_session import SqlAlchemyBase

# Привязка класса к таблице users
class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # Дата создания
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    # Всего правильных ответов на все вопросы
    total_correct_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    # Правильные ответы пользователя
    correct_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
