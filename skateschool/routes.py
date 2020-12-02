import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from skateschool import app, db, bcrypt
from skateschool.forms import RegistrationForm, LoginForm, UpdateProfileForm, PostForm, RequestResetForm, ResetPasswordForm, CommentForm
from skateschool.models import User, Posts, Comments
from flask_login import login_user, current_user, logout_user, login_required



@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    regForm = RegistrationForm()
    if regForm.submitOne.data and regForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(regForm.password.data).decode('utf-8')
        user = User(userFN=regForm.firstName.data, userSN=regForm.lastName.data, email=regForm.email.data, password=hashed_password, age=regForm.age.data,)
        db.session.add(user)
        db.session.commit()
        flash(f'Hello {regForm.firstName.data}, you are now signed up and can login!', 'success')
        return redirect(url_for('home'))
    loginForm = LoginForm()
    if loginForm.submitTwo.data and loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
            login_user(user, remember=loginForm.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('feed'))
        else:
            flash(f'Login unsuccessful. Please check email and password', 'danger')
    return render_template('home.html', title='Welcome', regForm=regForm, loginForm=loginForm)


def save_media(form_media):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_media.filename)
    media_fn = random_hex + f_ext
    media_path = os.path.join(app.root_path, 'static/postVideo', media_fn)
    form_media.save(media_path)

    return media_fn

@app.route('/feed', methods=['GET','POST'])
@login_required
def feed():
    postForm = PostForm()
    if postForm.validate_on_submit():
        if postForm.media.data != None:
            media_file=save_media(postForm.media.data)
            post = Posts(content=postForm.content.data, media=media_file, author=current_user)
        else:
            post = Posts(content=postForm.content.data, media=postForm.media.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been made!', 'success')
            return redirect(url_for('feed'))
    page = request.args.get('page', 1, type=int)
    posts=Posts.query.order_by(Posts.date.desc()).paginate(per_page=7)
    userImage = url_for('static', filename='profileImg/' + current_user.userImage)
    return render_template('feed.html', postForm=postForm, posts=posts, userImage=userImage)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profileImg', picture_fn)
    
    output_size = (150,150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

    # form_picture.save(picture_path)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    upForm = UpdateProfileForm() 
    if upForm.validate_on_submit():
        if upForm.userImage.data:
            picture_file = save_picture(upForm.userImage.data)
            current_user.userImage = picture_file
        current_user.userFN = upForm.firstName.data
        current_user.userSN = upForm.lastName.data
        current_user.email = upForm.email.data
        db.session.commit()
        flash('Your account was updated', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        upForm.firstName.data = current_user.userFN
        upForm.lastName.data = current_user.userSN
        upForm.email.data = current_user.email
    userImage = url_for('static', filename='profileImg/' + current_user.userImage)
    page = request.args.get('page', 1, type=int)
    posts=Posts.query.filter_by(author=current_user).order_by(Posts.date.desc()).paginate(per_page=3)
    return render_template('profile.html', title='Profile', userImage=userImage, upForm=upForm, posts=posts)

@app.route("/user/<string:userFN>")
def userPosts(userFN):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(userFN=userFN).first_or_404()
    posts=Posts.query.filter_by(author=user).order_by(Posts.date.desc()).paginate(per_page=7)
    return render_template('userPosts.html', posts=posts, user=user)


@app.route('/quiz')
@login_required
def quiz(): 
    return render_template('layout.html')

@app.route('/map')
@login_required
def map(): 
    userImage = url_for('static', filename='profileImg/' + current_user.userImage)
    return render_template('map.html', userImage=userImage)

@app.route('/post/update', methods=['GET','POST'])
@login_required
def new_post(): 
    postForm = PostForm()
    if postForm.validate_on_submit():
        flash('Your post has been updated!', 'success')
        return redirect(url_for('feed'))
    return render_template('updatePost.html', title='Update Post', postForm=postForm)

@app.route("/post/<int:post_id>", methods=['GET','POST'])
@login_required
def post(post_id):
    post = Posts.query.get_or_404(post_id)
    commentForm = CommentForm()
    if commentForm.validate_on_submit():
        comment = Comments(comment=commentForm.comment.data, user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted!', 'success')
        return redirect(url_for('post', post_id=post.id))
    page = request.args.get('page', 1, type=int)
    comments = Comments.query.filter_by(post_id=post.id).order_by(Comments.date.desc()).paginate(page=page, per_page=5)
    userImage = url_for('static', filename='profileImg/' + current_user.userImage)
    return render_template('post.html', post=post, userImage=userImage, commentForm=commentForm, comments=comments, post_id=post_id)


@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def updatePost(post_id):
    post = Posts.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    postForm = PostForm()
    if postForm.validate_on_submit():
        post.content = postForm.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        postForm.content.data = post.content
    userImage = url_for('static', filename='profileImg/' + current_user.userImage)
    return render_template('updatePost.html', title='Update Post', postForm=postForm, userImage=userImage, post=post)


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def deletePost(post_id):
    post = Posts.query.get_or_404(post_id)
    comments = Comments.query.filter_by(post_id=post.id).all()
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    for comments in comments:
        db.session.delete(comments)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('feed'))


# @app.route('/post/<int:post_id>delete_comment', methods=['POST'])
# @login_required
# def deleteComment(comment_id):
#     comment = Comments.query.get_or_404(comment_id)
#     if comment.author != current_user:
#         abort(403)
#     db.session.delete(comment)
#     db.session.commit()
#     flash('Your comment has been deleted!', 'success')
#     return redirect(url_for('feed'))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_reset_email(user):
    pass


@app.route('/reset_password', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    rrForm = RequestResetForm()
    if rrForm.validate_on_submit():
        user= User.query.filter_by(email=rrForm.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions on how to reset your password.', 'info')
        return redirect(url_for('home'))
    return render_template('reset_request.html', title='Reset Password', rrForm=rrForm)

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    rpForm = ResetPasswordForm()
    return render_template('reset_token.html', title='Reset Password', rpForm=rpForm)

     

