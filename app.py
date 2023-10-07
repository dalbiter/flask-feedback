from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import NewUserForm, UserLogin, AddFeedback, EditFeedback
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
            form.username.errors.append(f"Username {username} already exists, please choose another", "info")
            return render_template('register.html')
        
        session['username'] = new_user.username
        flash(f"Welcome {new_user.first_name}! You have successfully created your account!", "success")
        return  redirect(f'/users/{new_user.username}')

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
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ["Invalid username or password"]
            return render_template('login.html', form=form)
        
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user_details(username):
    """Verifies a user is logged in by checking session and shows secrets page"""
    
    if "username" not in session or session.get('username') != username:
        flash("You must be logged in to view this page", "danger")
        return redirect('/login')
    else:
        user = db.session.get(User, username)
        return render_template('user_details.html', user=user)

@app.route('/logout', methods=['POST'])
def logout_user():
    """log our user and flashes message"""
    user = db.session.get(User, session.get('username'))
    flash(f"Goodbye {user.first_name}, thanks for visiting!", "info")
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """deletes a user and all associated feedback"""

    user = User.query.get_or_404(username)

    if "username" not in session or session.get('username') != username:
        flash("You are not the owner of this account", "danger")
        return redirect('/login')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"We are sorry to see you go {user.first_name}. Your account has been successfully deleted", "info")
        session.pop('username')
        return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_user_feedback(username):
    """Displays form for a user to add feedback, updates db with new feedback"""
    if "username" not in session or session.get('username') != username:
        flash("Please login to add feedback", "danger")
        return redirect('/')
    form = AddFeedback()
    user = User.query.get_or_404(username)
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=session.get('username'))
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{username}')
    else:
        return render_template('add_feedback.html', form=form, user=user)

@app.route('/feedback/<int:fid>/update', methods=['GET', 'POST'])
def edit_user_feedback(fid):
    """displays form to edit user feedback and updates db accordingly"""
    
    feedback = Feedback.query.get_or_404(fid)

    if "username" not in session or session.get('username') != feedback.user.username:
        flash("Please login to edit feedback", "danger")
        return redirect('/')
    
    form = EditFeedback(obj=feedback)

    if form.validate_on_submit():
        title = form.title.data
        feedback.title = title if title else feedback.title
        content = form.content.data
        feedback.content = content if content else feedback.content
        db.session.commit()
        return redirect(f"/users/{session.get('username')}")
    else:
        return render_template('edit_feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<int:fid>/delete', methods=['POST'])
def delete_user_feedback(fid):
    """delete a users selected feedback"""

    feedback = Feedback.query.get_or_404(fid)

    if "username" not in session or session.get('username') != feedback.user.username:
        flash("Please login to delete feedback", "danger")
        return redirect('/')
    else:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{session.get('username')}")