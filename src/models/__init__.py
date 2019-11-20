from src import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())
    updated = db.Column(db.DateTime(timezone=True), server_default = db.func.now(), server_onupdate=db.func.now()) ## same as above, but with updating timestamp
    views_count = db.Column(db.Integer, default=0)

    def __repr__(self): 
        return '<Task>' % self.id

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)
    avatar_url = db.Column(db.Text)
    birthday = db.Column(db.DateTime(timezone=True))
    admin = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    def __repr__(self):
        return '<Task>' % self.id

    def generate_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_email(self, email):
        return User.query.filter_by(email = email).first()

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())
    updated = db.Column(db.DateTime(timezone=True), server_default = db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<Task>' % self.id

class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    def __repr__(self):
        return '<Task>' % self.id

class Thumbsup(db.Model):
    __tablename__ = "thumbsups"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    def __repr__(self):
        return '<Task>' % self.id

class Thumbsdown(db.Model):
    __tablename__ = "thumbsdowns"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    def __repr__(self):
        return '<Task>' % self.id        

class Follow(db.Model):
    __tablename__ = "follows"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default = db.func.now())

    def __repr__(self):
        return '<Task>' % self.id
