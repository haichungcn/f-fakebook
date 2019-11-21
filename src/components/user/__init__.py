from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from src.models import User, Post, Comment, Follow, Like, Thumbsdown, Thumbsup
from src import db



user_blueprint = Blueprint('user', __name__, template_folder='../../templates')


@user_blueprint.route("/<id>/posts", methods=['GET'])
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

    return render_template("user/userfeed.html",
        user = thisUser,
        posts = posts,
        comments = comments,
        follows = follows)

@user_blueprint.route("/<id>/follow", methods=['GET', 'POST'])
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
    return redirect(url_for("user.userposts", id = id))

