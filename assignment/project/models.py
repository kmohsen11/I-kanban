from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    status = db.Column(db.String(20), default='todo')
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', back_populates='tasks', foreign_keys=[user_id])
    parent = db.relationship('Task', remote_side=[id], back_populates='subtasks', uselist=False)
    subtasks = db.relationship('Task', back_populates='parent', cascade='all')

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
