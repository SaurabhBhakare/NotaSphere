import os
import config
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import time
from .models import User, Note, Category
from .forms import RegisterForm, LoginForm, NoteForm
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, and_

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    category = Category.query.all()
    if current_user.is_authenticated:
        favorite_notes = Note.query.filter_by(user_id=current_user.id, status=True, favorite=True).all()
        gallery = Note.query.filter(or_(and_(Note.user_id == current_user.id, Note.status == True),
                                        and_(Note.user_id != current_user.id, Note.publish == True,
                                             Note.status == True))).all()
    else:
        favorite_notes = None
        gallery = None
    published_notes = Note.query.filter_by(status=True, publish=True).all()
    return render_template('home.html', published_notes=published_notes, favorite_notes=favorite_notes, gallery=gallery)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']
        img = request.files.get('image')
        print("Got img from request:", img)

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Please choose a different one.', 'danger')
            return redirect(url_for('main.register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered with us. Please choose different one.', 'danger')
            return redirect(url_for('main.register'))

        if password1 != password2:
            flash('Password & Confirm password does not matched', 'danger')
            return redirect(url_for('main.register'))

        img_filename = None
        if img and allowed_file(img.filename):
            print("Inside if file name..")
            safe_name = secure_filename(img.filename)
            img_filename = f"{username}_{int(time.time())}_{safe_name}"
            img.save(os.path.join(current_app.config['UPLOAD_PROFILE'], img_filename))

        hashed_pw = generate_password_hash(password1)
        user = User(username=username, name=name, email=email, image_file=img_filename, password=hashed_pw)
        db.session.add(user)
        print("saved to database..")
        db.session.commit()
        flash('User register successfully..😊', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password1']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Login failed..😑', 'danger')
    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))
    logout_user()
    return redirect(url_for('main.home'))


@main.route('/required_login')
def required_login():
    return render_template('required_login.html')


@main.route('/dashboard', methods=['GET', 'POST'])
# @login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))

    notes = Note.query.filter_by(user_id=current_user.id, status=True).order_by(Note.created_at.desc()).all()
    all_category = Category.query.all()
    return render_template('dashboard.html', notes=notes, all_category=all_category, view_type="all")


@main.route('/category/<int:cat_id>')
def category_notes(cat_id):
    notes = Note.query.filter_by(user_id=current_user.id, category_id=cat_id, status=True).all()
    category_name = Category.query.filter_by(id=cat_id).first()
    all_category = Category.query.all()
    return render_template("dashboard.html", notes=notes, all_category=all_category, category_name=category_name,
                           view_type="category")


@main.route('/favorites')
def favorite_notes():
    notes = Note.query.filter_by(user_id=current_user.id, favorite=True, status=True).all()
    all_category = Category.query.all()
    return render_template("dashboard.html", notes=notes, all_category=all_category, view_type="favorites")


@main.route('/published')
def published_notes():
    notes = Note.query.filter_by(user_id=current_user.id, status=True, publish=True).all()
    all_category = Category.query.all()
    return render_template("dashboard.html", notes=notes, all_category=all_category, view_type="published")


@main.route('/trash')
def deleted_notes():
    notes = Note.query.filter_by(user_id=current_user.id, status=False).all()
    all_category = Category.query.all()
    return render_template("dashboard.html", notes=notes, all_category=all_category, view_type="deleted")


@main.route('/note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def view_note(note_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))
    note = Note.query.get_or_404(note_id)
    return render_template('note.html', note=note)


@main.route('/category/new', methods=['GET', 'POST'])
@login_required
def create_category():
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))
    if request.method == "POST":
        new_category = request.form['title'].title()
        img = request.files.get('image')
        existing_category = Category.query.filter_by(name=new_category).first()
        if existing_category:
            flash('Category already exists.', 'danger')
            return redirect(url_for('main.create_category'))

        img_filename = None
        if img and allowed_file(img.filename):
            safe_name = secure_filename(img.filename)
            img_filename = f"{current_user.id}_{int(time.time())}_{safe_name}"
            img.save(os.path.join(current_app.config['UPLOAD_CATEGORY'], img_filename))

        try:
            category = Category(name=new_category, image_file=img_filename)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully..!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Something went wrong. try after some time.', 'danger')
        return redirect(url_for('main.create_category'))

    return render_template('create_category.html')


@main.route('/note/new', methods=['GET', 'POST'])
@login_required
def create_note():
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))
    all_category = Category.query.all()
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        img = request.files.get('image')
        try:
            if request.form['publish']:
                publish = True
        except:
            publish = False

        img_filename = None
        if img and allowed_file(img.filename):
            safe_name = secure_filename(img.filename)
            img_filename = f"{current_user.id}_{int(time.time())}_{safe_name}"
            img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], img_filename))

        try:
            note = Note(title=title, content=content, image_file=img_filename, user_id=current_user.id,
                        category_id=category, status=True, publish=publish)
            db.session.add(note)
            db.session.commit()
            flash('Note added successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Something went wrong. try after some time.' + str(e), 'danger')
            return redirect(url_for('main.create_note'))
    return render_template('create_note.html', category=all_category)


@main.route('/note/<int:note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))

    note = Note.query.get_or_404(note_id)
    all_category = Category.query.all()

    if note.user != current_user:
        return redirect(url_for('main.dashboard'))
    if request.method == "POST":
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        img = request.files.get('image')
        try:
            if request.form['publish']:
                publish = True
        except:
            publish = False
        try:
            if request.form['favorite']:
                favorite = True
        except:
            favorite = False

        img_filename = None
        if img and allowed_file(img.filename):
            safe_name = secure_filename(img.filename)
            img_filename = f"{current_user.id}_{int(time.time())}_{safe_name}"
            img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], img_filename))

        note.title = title
        note.category_id = category
        note.content = content
        note.updated_at = datetime.utcnow()
        # note.image_file = img
        note.publish = publish
        note.favorite = favorite
        db.session.commit()
        flash('Note edited successfully..!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_note.html', note=note, all_category=all_category)


@main.route('/note/<int:note_id>/trash')
@login_required
def trash_note(note_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))
    note = Note.query.get_or_404(note_id)
    if note.user == current_user:
        note.status = False
        db.session.commit()
        flash('Note deleted successfully..', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/note/<int:note_id>/delete')
@login_required
def delete_note(note_id):
    if not current_user.is_authenticated:
        return redirect(url_for('main.required_login'))
    note = Note.query.get_or_404(note_id)
    if note.user == current_user:
        db.session.delete(note)
        db.session.commit()
        flash('Note permanently deleted..', 'success')
    return redirect(url_for('main.dashboard'))


@main.route('/note/<int:note_id>/restore')
@login_required
def restore_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user == current_user:
        note.status = True
        db.session.commit()
        flash('Note Restored successfully...', 'success')
    return redirect(url_for('main.dashboard'))


def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in config.Config.ALLOWED_EXTENSIONS


@main.route('/contact')
@login_required
def contact():
    if current_user.is_authenticated:
        return render_template('contact.html')
    return redirect(url_for('main.required_login'))


@main.route('/profile')
@login_required
def my_profile():
    user = current_user
    return render_template('profile.html',user=user)
