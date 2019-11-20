import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, logout_user, login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# setup flask migration
migrate = Migrate(app, db)

# setup Flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" #redirect to login function if user not logged in



## Create all tables in db
db.create_all()

from src.model import User, Post
## Setup login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

## Controllers:
@app.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for("postfeed", sort = "newest"))
    return redirect(url_for('login'))

from src.components.post import post_blueprint
app,register_blueprint(post_blueprint, url_prefix='/post')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User()
        user = user.check_email(request.form['email'])
        if user:
            if user.check_password(request.form['password']):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Invalid password", "danger")
                redirect(url_for("login"))
        else:
            flash("Can not find user", "danger")
            redirect(url_for("login"))
    
    return render_template("views/login.html")

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        user = User()
        user = user.check_email(request.form['email'])
        if not user:
            new_user = User(
                username = request.form['username'],
                email = request.form['email'],
                avatar_url = request.form['avatar_url']
                )
            new_user.generate_password(request.form['password'])
            db.session.add(new_user)
            db.session.commit()
            flash("successfully added user {0}".format(new_user.username), "success")
            return redirect(url_for('home'))
        else:
            flash("Username is already exist", "warning")
    
    return render_template("views/signup.html")

@app.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/user/<id>", methods=['GET'])
@login_required
def userposts(id):
    thisUser = User.query.get(id)
    thisUser.followed = Follow.query.filter_by(user_id = id).count()
    thisUser.following = Follow.query.filter_by(author = id).count()
    thisUser.comments = Comment.query.filter_by(author = id).count()
    thisUser.likes = 0
    thisUser.thumbsUps = 0
    thisUser.thumbsDowns = 0

    posts = Post.query.filter_by(author = id).order_by(Post.timestamp.desc()).all()
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    follows = Follow.query.filter_by(author = current_user.id).all()

    for post in posts:
        user = User.query.get(post.author)
        post.username = user.username
        post.avatar_url = user.avatar_url
        post.comments = Comment.query.filter_by(post_id = post.id).count()
        post.likes = Like.query.filter_by(post_id = post.id).count()
        thisUser.likes = thisUser.likes + post.likes
        post.thumbsUps = Thumbsup.query.filter_by(post_id = post.id).count()
        thisUser.thumbsUps = thisUser.thumbsUps + post.thumbsUps
        post.thumbsDowns = Thumbsdown.query.filter_by(post_id = post.id).count()
        thisUser.thumbsDowns = thisUser.thumbsDowns + post.thumbsDowns
        post.currentUserLike = Like.query.filter_by(author = current_user.id, post_id = post.id).first()
        post.currentUserThumbsUp = Thumbsup.query.filter_by(author = current_user.id, post_id = post.id).first()
        post.currentUserThumbsDown = Thumbsdown.query.filter_by(author = current_user.id, post_id = post.id).first()

    for comment in comments:
        user = User.query.get(comment.author)
        comment.username = user.username
        comment.avatar_url = user.avatar_url

    return render_template("views/userfeed.html",
        user = thisUser,
        posts = posts,
        comments = comments,
        follows = follows)

@app.route("/user/<id>/follow", methods=['GET', 'POST'])
@login_required
def follow(id):
    if request.method =='POST':
        if current_user.id == id :
            flash("Sorry, you can't follow yourself", "success")
        else:
            follow = Follow.query.filter_by(author = current_user.id, user_id = id).first()
            if not follow:
                new_follow = Follow(author = current_user.id, user_id = id)
                db.session.add(new_follow)
                db.session.commit()
                flash("Successfully followed user", "success")
            if follow:
                db.session.delete(follow)
                db.session.commit()
                flash("Successfully unfollowed user", "success")
    return redirect(url_for("userposts", id = id))

@app.route("/statistics", methods=['GET', 'POST'])
@login_required
def statistics():
    print('run statistics')
    posts = Post.query.all()
    users = User.query.all()
    for post in posts:
        post.likes = Like.query.filter_by(post_id = post.id).count()
        post.thumbsups = Thumbsup.query.filter_by(post_id = post.id).count()
        post.thumbsdowns = Thumbsdown.query.filter_by(post_id = post.id).count()
        post.comments = Comment.query.filter_by(post_id = post.id).count()
        user = User.query.get(post.author)
        post.username = user.username
        post.avatar_url = user.avatar_url
    posts_likes = sorted(posts, key = lambda i : i.likes, reverse = True)[:3]
    posts_thumbsups = sorted(posts, key = lambda i : i.thumbsups, reverse = True)[:3]
    posts_thumbsdowns = sorted(posts, key = lambda i : i.thumbsdowns, reverse = True)[:3]
    posts_comments = sorted(posts, key = lambda i : i.comments, reverse = True)[:3]

    for user in users:
        user.follows = Follow.query.filter_by(user_id = user.id).count()
    users_follows = sorted(users, key = lambda i : i.follows, reverse = True)[:3]

    return render_template("views/statistics.html",
                            posts_likes = posts_likes,
                            posts_thumbsups = posts_thumbsups,
                            posts_thumbsdowns = posts_thumbsdowns,
                            posts_comments = posts_comments,
                            users_follows = users_follows)


if __name__ == "__main__":
    app.run(debug = True)