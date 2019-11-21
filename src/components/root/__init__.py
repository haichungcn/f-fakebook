from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from src.models import User, Post, Comment, Follow, Like, Thumbsdown, Thumbsup
from src import db, app
from itsdangerous import URLSafeTimedSerializer
import requests


root_blueprint = Blueprint('root', __name__, template_folder='../../templates')

def send_email(token, email, name):
    url="https://api.mailgun.net/v3/mg.haifly.dev/messages"
    try:
        response = requests.post(url,
                auth=('api', app.config['EMAIL_API']),
                data={'from': 'THE HIGHTABLE OF HFBOOK <admin@hfbook.com>',
                'to': [email],
                'subject': 'HFBOOK Reset Password',
                'text': f"""Hi {name}, pleaser click on this link to create new password:\nhttps://haic-fbook.herokuapp.com//resetpassword/{token} \n This link only valid for 15 minutes so please hurry!"""}
            )
        response.raise_for_status()
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')

@root_blueprint.route("/forgetpassword", methods=['GET', 'POST'])
def forget():
    if current_user.is_authenticated:
        return redirect(url_for('root.home'))
    if request.method == 'POST':
        user = User(email = request.form['email']).check_email(request.form['email'])
        if not user:
            flash('Invalid Email', 'danger')
            return redirect(url_for('root.forget'))
        s = URLSafeTimedSerializer(app.secret_key)
        token = s.dumps(user.email, salt="RESET_PASSWORD")
        print(token)
        send_email(token, user.email, user.username)

        flash('Thank you for submit, Please check your email box (or spam box) within 15 minutes.', 'success')
        return redirect(url_for('root.login'))
    return render_template('root/forgetpassword.html')

@root_blueprint.route("/resetpassword/<token>", methods=['GET', 'POST'])
def resetpw(token):
    if current_user.is_authenticated:
        return redirect(url_for('root.home'))
    s = URLSafeTimedSerializer(app.secret_key)
    email = s.loads(token, salt="RESET_PASSWORD", max_age=900)
    user = User(email = email).check_email(email)
    if not user:
        flash('Invalid link, please try again', 'danger')
        return redirect(url_for('root.forget'))
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm']:
            flash('Please enter the right confirm password', 'danger')
            return redirect(url_for('root.resetpw', token=token))
        user.generate_password(request.form['password'])
        db.session.commit()
    return render_template("root/resetpassword.html", token = token)
            

@root_blueprint.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for("post.postfeed", filter = "most-recent"))
    return redirect(url_for('root.login'))

@root_blueprint.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User()
        user = user.check_email(request.form['email'])
        if user:
            if user.check_password(request.form['password']):
                login_user(user)
                return redirect(url_for("root.home"))
            else:
                flash("Invalid password", "danger")
                redirect(url_for("root.login"))
        else:
            flash("Can not find user", "danger")
            redirect(url_for("root.login"))
    
    return render_template("root/login.html")

@root_blueprint.route("/signup", methods=['GET','POST'])
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
            return redirect(url_for('root.home'))
        else:
            flash("Username is already exist", "warning")
    
    return render_template("root/signup.html")

@root_blueprint.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for('root.home'))

@root_blueprint.route("/statistics", methods=['GET', 'POST'])
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

    return render_template("root/statistics.html",
                            posts_likes = posts_likes,
                            posts_thumbsups = posts_thumbsups,
                            posts_thumbsdowns = posts_thumbsdowns,
                            posts_comments = posts_comments,
                            users_follows = users_follows)