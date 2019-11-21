from flask import Blueprint, request, url_for, render_template, redirect, flash
from flask_login import current_user, login_user, login_required, logout_user
from src.models import User, Post, Comment, Follow, Like, Thumbsdown, Thumbsup
from src import db



post_blueprint = Blueprint('post', __name__, template_folder='../../templates')



@post_blueprint.route('/feed', methods=['GET'])
@login_required
def postfeed():
    if request.args.get('filter') == 'most-recent':
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    elif request.args.get('filter') == 'oldest':
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
    
    return render_template("post/postfeed.html",
        posts = posts,
        comments = comments,
        follows = follows,
        users = users)

@post_blueprint.route("/", methods=['GET','POST'])
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
            return redirect(url_for('root.home'))
        else: flash('User try to post an empty post', 'warning')
    return redirect(url_for('root.home'))

@post_blueprint.route('/<id>', methods=['GET', 'POST'])
@login_required
def singlepost(id):
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
    
    return render_template("post/singlepost.html",
        post = post,
        comments = comments,
        users = users)

@post_blueprint.route("/<id>/edit", methods=['GET', 'POST'])
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
            return redirect(url_for('root.home'))
        else:
            flash("You can't leave the body empty", "warning")
    return redirect(url_for('root.home'))

@post_blueprint.route("/<id>/delete", methods=['GET', 'POST'])
@login_required
def deletepost(id):
    if request.method == 'POST':
        post = Post.query.get(id)
        if not post:
            flash("CAN'T NOT FIND YOUR POST", 'danger')
            return redirect(url_for('root.home'))
        db.session.delete(post)
        db.session.commit()
        flash("Successfully deleted post", 'success')
        return redirect(url_for('root.home'))
    return "404"
    

@post_blueprint.route("/<id>/comment", methods=['GET','POST'])
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
            return redirect(url_for('root.home'))
        else: flash('User try to post an empty comment', 'warning')
    return redirect(url_for('root.home'))

@post_blueprint.route("/<id>/comment/<cid>/edit", methods=['GET', 'POST'])
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
            return redirect(url_for('root.home'))
        else:
            flash("You can't leave the body empty", "warning")
    return redirect(url_for('root.home'))

@post_blueprint.route("/<id>/comment/<cid>/delete", methods=['GET', 'POST'])
@login_required
def deletecomment(id, cid):
    if request.method == 'POST':
        comment = Comment.query.get(cid)
        if not comment:
            flash("can't find your comment", 'danger')
            return redirect(url_for('root.home'))
        db.session.delete(comment)
        db.session.commit()
        flash("Successfully deleted comment", 'success')
        return redirect(url_for('root.home'))
    return "404"

@post_blueprint.route("/<id>/like", methods=['GET', 'POST'])
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
    return redirect(url_for("root.home"))

@post_blueprint.route("/<id>/thumbsup", methods=['GET', 'POST'])
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
    return redirect(url_for("root.home"))

@post_blueprint.route("/<id>/thumbsdown", methods=['GET', 'POST'])
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
    return redirect(url_for("root.home"))