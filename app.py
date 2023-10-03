from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import NewUserForm, UserLogin
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'abc123'
app.config['DEBUG_TB_INTERECEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Registers a new user"""

    form = NewUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append(f"Username {username} already exists, please choose another")
            return render_template('register.html')
        
        session['username'] = new_user.username
        flash(f"Welcome {new_user.first_name}! You have successfully created your account!", "success")
        return  redirect('/secrets')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Logs in a user"""

    form = UserLogin()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome back {user.first_name}!", "success")
            session['username'] = user.username
            return redirect('/secrets')
        else:
            form.username.errors = ["Invalid username or password"]
            return render_template('login.html', form=form)
        
    return render_template('login.html', form=form)

@app.route('/secrets')
def show_secrets():
    """Verifies a user is logged in by checking session and shows secrets page"""
    if "username" not in session:
        flash("You must be logged in to view this page")
        return redirect('/login')
    else:
        return render_template('secrets.html')

@app.route('/logout', methods=['POST'])
def logout_user():
    """log our user and flashes message"""
    user = db.session.get(User, session.get('username'))
    flash(f"Goodbye {user.first_name}, thanks for visiting!", "info")
    session.pop('username')
    return redirect('/')