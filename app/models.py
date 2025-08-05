from datetime import datetime
from flask_login import UserMixin

from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(256), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    # notes = db.relationship('Note', backref='category', lazy=True)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='notes')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='notes')

    favorite = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=False)
    publish = db.Column(db.Boolean, default=False)

    @property
    def time_since_created(self):
        delta = datetime.utcnow() - self.updated_at
        seconds = delta.total_seconds()

        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds // 60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds // 3600)} hours ago"
        elif seconds < 2592000:
            return f"{int(seconds // 86400)} days ago"
        else:
            return f"{int(seconds // 2592000)} months ago"