from enum import unique

from sqlalchemy.orm import backref
from app import db
from flask_login import UserMixin
from app import login
import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwordHash = db.Column(db.String(200))
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

class Post( db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100),  nullable=False)
    content = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy=True)
    def __repr__(self):
        return '<Post Title: {}>'.format(self.title)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    def __repr__(self):
        return '<Comment: {}>'.format(self.comment)
        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
