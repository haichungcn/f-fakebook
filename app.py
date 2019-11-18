from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, logout_user, login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Super Secret'

db = SQLAlchemy(app)

# setup flask migration
migrate = Migrate(app, db)

# setup Flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" #redirect to login function if user not logged in


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

## Create all tables in db
db.create_all()

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

@app.route('/postfeed/<sort>', methods=['GET'])
@login_required
def postfeed(sort):
    if sort == "newest":
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    elif sort == "oldest":
        posts = Post.query.order_by(Post.timestamp.asc()).all()
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    follows = Follow.query.filter_by(author = current_user.id).all()
    current_user.posts = Post.query.filter_by(author = current_user.id).count()
    current_user.likes = 0;
    current_user.thumbsUps = 0;
    current_user.thumbsDowns = 0;
    current_user.comments = Comment.query.filter_by(author = current_user.id).count()
    current_user.followed = Follow.query.filter_by(user_id = current_user.id).count()
    current_user.following = Follow.query.filter_by(author = current_user.id).count()
    users = User.query.all()

    for post in posts:
        user = User.query.get(post.author)
        post.username = user.username
        post.avatar_url = user.avatar_url
        post.comments = Comment.query.filter_by(post_id = post.id).count()
        post.likes = Like.query.filter_by(post_id = post.id).count()
        post.thumbsUps = Thumbsup.query.filter_by(post_id = post.id).count()
        post.thumbsDowns = Thumbsdown.query.filter_by(post_id = post.id).count()
        if post.author == current_user.id:
            current_user.likes = current_user.likes + post.likes
            current_user.thumbsUps = current_user.thumbsUps + post.thumbsUps
            current_user.thumbsDowns = current_user.thumbsDowns + post.thumbsDowns
        post.currentUserLike = Like.query.filter_by(author = current_user.id, post_id = post.id).first()
        post.currentUserThumbsUp = Thumbsup.query.filter_by(author = current_user.id, post_id = post.id).first()
        post.currentUserThumbsDown = Thumbsdown.query.filter_by(author = current_user.id, post_id = post.id).first()

    for comment in comments:
        user = User.query.get(comment.author)
        comment.username = user.username
        comment.avatar_url = user.avatar_url
    
    return render_template("views/postfeed.html",
        posts = posts,
        comments = comments,
        follows = follows,
        users = users)

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

@app.route("/post", methods=['GET','POST'])
@login_required
def post():
    if request.method == 'POST':
        if request.form['body'] != '':
            new_post = Post(
                body = request.form['body'],
                author = current_user.id
            )
            if 'image_url' in request.form:
                new_post.image_url = request.form['image_url']
            db.session.add(new_post)
            db.session.commit()
            flash('Successfully posted', 'success')
            return redirect(url_for('home'))
        else: flash('User try to post an empty post', 'warning')
    return redirect(url_for('home'))

@app.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def siunglepost(id):
    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id = id).all()
    current_user.likes = 0
    current_user.thumbsUps = 0
    current_user.thumbsDowns = 0
    users = User.query.all()

    user = User.query.get(post.author)
    post.views_count += 1
    db.session.commit()
    post.username = user.username
    post.avatar_url = user.avatar_url
    post.comments = Comment.query.filter_by(post_id = post.id).count()
    post.likes = Like.query.filter_by(post_id = post.id).count()
    post.thumbsUps = Thumbsup.query.filter_by(post_id = post.id).count()
    post.thumbsDowns = Thumbsdown.query.filter_by(post_id = post.id).count()
    if post.author == current_user.id:
        current_user.likes = current_user.likes + post.likes
        current_user.thumbsUps = current_user.thumbsUps + post.thumbsUps
        current_user.thumbsDowns = current_user.thumbsDowns + post.thumbsDowns
    post.currentUserLike = Like.query.filter_by(author = current_user.id, post_id = post.id).first()
    post.currentUserThumbsUp = Thumbsup.query.filter_by(author = current_user.id, post_id = post.id).first()
    post.currentUserThumbsDown = Thumbsdown.query.filter_by(author = current_user.id, post_id = post.id).first()

    for comment in comments:
        user = User.query.get(comment.author)
        comment.username = user.username
        comment.avatar_url = user.avatar_url
    
    return render_template("views/singlepost.html",
        post = post,
        comments = comments,
        users = users)

@app.route("/post/<id>/edit", methods=['GET', 'POST'])
@login_required
def editpost(id):
    if request.method == 'POST':
        if request.form['body'] :
            post = Post.query.get(id)
            post.body = request.form['body']
            if "image_url" in request.form:
                post.image_url = request.form['image_url']
            db.session.commit()
            flash("successfully edited post", "success")
            return redirect(url_for('home'))
        else:
            flash("You can't leave the body empty", "warning")
    return redirect(url_for('home'))

@app.route("/post/<id>/delete", methods=['GET', 'POST'])
@login_required
def deletepost(id):
    if request.method == 'POST':
        post = Post.query.get(id)
        if not post:
            flash("CAN'T NOT FIND YOUR POST", 'danger')
            return redirect(url_for('home'))
        db.session.delete(post)
        db.session.commit()
        flash("Successfully deleted post", 'success')
        return redirect(url_for('home'))
    return "404"
    

@app.route("/post/<id>/comment", methods=['GET','POST'])
@login_required
def comment(id):
    if request.method == 'POST':
        if request.form['body'] != '':
            new_comment = Comment(
                body = request.form['body'],
                author = current_user.id,
                post_id = id
            )
            if 'image_url' in request.form:
                new_comment.image_url = request.form['image_url']
            db.session.add(new_comment)
            db.session.commit()
            flash('Successfully posted comment', 'success')
            return redirect(url_for('home'))
        else: flash('User try to post an empty comment', 'warning')
    return redirect(url_for('home'))

@app.route("/post/<id>/comment/<cid>/edit", methods=['GET', 'POST'])
@login_required
def editcomment(id, cid):
    if request.method == 'POST':
        if request.form['body'] and cid :
            comment = Comment.query.get(cid)
            comment.body = request.form['body']
            if "image_url" in request.form:
                comment.image_url = request.form['image_url']
            db.session.commit()
            flash("successfully edited post", "success")
            return redirect(url_for('home'))
        else:
            flash("You can't leave the body empty", "warning")
    return redirect(url_for('home'))

@app.route("/post/<id>/comment/<cid>/delete", methods=['GET', 'POST'])
@login_required
def deletecomment(id, cid):
    if request.method == 'POST':
        comment = Comment.query.get(cid)
        if not comment:
            flash("can't find your comment", 'danger')
            return redirect(url_for('home'))
        db.session.delete(comment)
        db.session.commit()
        flash("Successfully deleted comment", 'success')
        return redirect(url_for('home'))
    return "404"

@app.route("/post/<id>/like", methods=['GET', 'POST'])
@login_required
def likePost(id):
    if request.method == 'POST':
        like = Like.query.filter_by(author = current_user.id, post_id = id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            flash('Successfully unliked post', 'success')
        else:
            new_like = Like(author = current_user.id, post_id = id)
            db.session.add(new_like)
            db.session.commit()
            flash('Successfully liked post', 'success')
    return redirect(url_for("home"))

@app.route("/post/<id>/thumbsup", methods=['GET', 'POST'])
@login_required
def thumbsUpPost(id):
    if request.method == 'POST':
        thumbsup = Thumbsup.query.filter_by(author = current_user.id, post_id = id).first()
        thumbsdown = Thumbsdown.query.filter_by(author = current_user.id, post_id = id).first()
        if not thumbsup:
            new_thumbsup = Thumbsup(author = current_user.id, post_id = id)
            db.session.add(new_thumbsup)
            db.session.commit()
            flash('Successfully thumbed up post', 'success')
            if thumbsdown:
                db.session.delete(thumbsdown)
                db.session.commit()
        if thumbsup:
            db.session.delete(thumbsup)
            db.session.commit()
            flash('Successfully unthumbed up post', 'success')
    return redirect(url_for("home"))

@app.route("/post/<id>/thumbsdown", methods=['GET', 'POST'])
@login_required
def thumbsDownPost(id):
    if request.method == 'POST':
        thumbsdown = Thumbsdown.query.filter_by(author = current_user.id, post_id = id).first()
        thumbsup = Thumbsup.query.filter_by(author = current_user.id, post_id = id).first()
        if not thumbsdown:
            new_thumbsdown = Thumbsdown(author = current_user.id, post_id = id)
            db.session.add(new_thumbsdown)
            db.session.commit()
            flash('Successfully thumbed down post', 'success')
            if thumbsup:
                db.session.delete(thumbsup)
                db.session.commit()
        if thumbsdown:
            db.session.delete(thumbsdown)
            db.session.commit()
            flash('Successfully unthumbed down post', 'success')
    return redirect(url_for("home"))

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