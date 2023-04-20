import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from data_db.db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, UserMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answers = orm.relationship("Answer", back_populates='question')

    def is_radio(self):
        return self.type == 'radio'
