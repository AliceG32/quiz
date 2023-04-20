import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey
from sqlalchemy import orm

from data_db.db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase, UserMixin):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    question_id = Column(sqlalchemy.Integer, ForeignKey('questions.id'))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    question = orm.relationship('Question')
