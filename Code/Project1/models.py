from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    username = db.Column(String(255), unique=True, nullable=False)
    email = db.Column(String(255), unique=True, nullable=False)
    password_hash = db.Column(Text, nullable=False)
    role = db.Column(Enum('admin', 'author', 'reader', name='user_roles'), default='reader', nullable=False)

    posts = relationship('Post', back_populates='author')

    comments = relationship('Comment', back_populates='user')


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    title = db.Column(String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    author_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = db.Column(DateTime, default=func.now(), nullable=False)

    author = relationship('User', back_populates='posts')

    comments = relationship('Comment', back_populates='post', cascade="all, delete-orphan")


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    content = db.Column(Text, nullable=False)
    post_id = db.Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = db.Column(DateTime, default=func.now(), nullable=False)

    post = relationship('Post', back_populates='comments')


    user = relationship('User', back_populates='comments')
