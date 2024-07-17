from flask import Flask, redirect, render_template, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
app = Flask(__name__)
app.secret_key = '89H9'  

base_dir = os.path.abspath(os.path.dirname(__file__))  # current directory
database_path = os.path.join(base_dir, 'todo.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title} - {self.desc}"
    
@app.route('/profile')
def profile():
    return render_template('profile.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and (user.password == password):  # Securely compare passwords
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Use Flask-Login to register the user
        login_user(new_user)

        flash('Registration successful! You are now logged in.')
        return redirect(url_for('login'))  

    return render_template('register.html')

@app.route('/MyToDo', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        # Access the currently logged-in user using current_user
        user = current_user

        # Option 1: Associate todo with the logged-in user (recommended)
        todo = Todo(title=title, desc=desc, user_id=user.id)

        # Option 2: Access username for display purposes only
        username = user.username  # This doesn't change data association

        db.session.add(todo)
        db.session.commit()
        return redirect('/')

    alltodo = Todo.query.all()
    return render_template('index.html', alltodo=alltodo)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/delete/<int:sno>')
@login_required
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect("/")

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
@login_required
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo.title = title
        todo.desc = desc
        db.session.commit()
        return redirect("/")
    return render_template('update.html', todo=todo)

if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("Database and tables created!")
        except Exception as e:
            print(f"An error occurred: {e}")

    app.run(debug=True)
