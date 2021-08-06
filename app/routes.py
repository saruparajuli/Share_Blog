import bcrypt
from flask.helpers import url_for
from flask.templating import render_template
from flask_login.utils import login_required, logout_user
from werkzeug.utils import redirect
from app import app, db, bcrypt, login
from app.forms import LoginForm, RegisterForm, CreatePostForm, CommentForm
from flask import flash, request
from flask_login import login_user, current_user
from app.models import Comment, User, Post

@login.unauthorized_handler
def unauthorized_callback():
    flash('You are not authorised to do this.')
    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        password = form.password.data
        pw_hash = bcrypt.generate_password_hash(password)
        user = User(username=form.username.data, email=form.email.data ,passwordHash=pw_hash)
        db.session.add(user)
        db.session.commit()
        return(redirect(url_for('login')))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not bcrypt.check_password_hash(user.passwordHash, form.password.data):
            flash('Your username or password is incorrect.')
            return redirect(url_for('login'))
        login_user(user, remember=True)
        return redirect(url_for('userPage', name=user.username))
    return render_template('login.html', form=form)

@app.route('/<name>', methods=['GET', 'POST'])
def userPage(name):
    form = CreatePostForm()
    if current_user.is_authenticated:
        if current_user.username == name:
            if form.validate_on_submit():
                form.content.data = request.form['content']
                post = Post(title=form.title.data,content=form.content.data, user_id=current_user.id)
                db.session.add(post)
                db.session.commit()
                return redirect(url_for('userPage', name=name))
    user = User.query.filter_by(username=name).first()
    if user:
        posts = Post.query.filter_by(user_id=user.id).all()
        return render_template('userPage.html', name=name, form=form, posts=posts)
    else:
        return redirect(url_for('index'))

@app.route("/delete/<post_id>")
def delete(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        if current_user.is_authenticated:
            if post.user_id == current_user.id:
                db.session.delete(post)
                db.session.commit()
                return redirect(url_for('userPage', name=current_user.username))
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/update/<post_id>', methods=['GET', 'POST'])
@login_required
def update(post_id):
    form = CreatePostForm()
    post = Post.query.filter_by(id=post_id).first()
    if post:
        if request.method == 'GET':
            if current_user.is_authenticated:
                if post.user_id == current_user.id:
                    form.title.data = post.title
                    form.content.data = post.content
                    return render_template('edit_post.html', form=form)
        if request.method == 'POST':
            if form.validate_on_submit():
                print('success')
                post.title = form.title.data
                post.content = request.form['content']
                db.session.commit()
                return redirect(url_for('userPage', name=current_user.username))

    return redirect(url_for('index'))

@app.route("/<post_username>/<post_id>", methods=['GET', 'POST'])
def post(post_id, post_username):
    form = CommentForm()
    post = Post.query.filter_by(id=post_id).first()
    comments = Comment.query.filter_by(post_id=post.id).all()
    if request.method == 'GET':
        return render_template('post.html', post=post, form=form, comments=comments)
    if request.method == 'POST':
        if form.validate_on_submit:
            form.content.data = request.form['content']
            comment = Comment(comment=form.content.data, user_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('post', post_id=post.id, post_username=post.user.username))

@app.route("/delete/<post_id>/<comment_id>", methods=['GET', 'POST'])
@login_required
def deleteComment(comment_id, post_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    post = Post.query.filter_by(id = post_id).first()
    if comment:
        if comment.user_id == current_user.id:
            db.session.delete(comment)
            db.session.commit()
            return (redirect(url_for('post', post_id=comment.post_id, post_username=post.user.username)))
    return redirect(url_for('post', post_id=post.id, post_username=post.user.username))

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
