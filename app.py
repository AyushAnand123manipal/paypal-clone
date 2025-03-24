from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, bcrypt, User, Transaction
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:your_mysql_password@localhost/paypal_clone'  # Replace with your credentials
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To suppress a warning

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Page (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Registration Page (register.html)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Page (login.html)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

# Dashboard Page (dashboard.html)
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Send Money Page (payments.html)
@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    if request.method == 'POST':
        recipient_email = request.form['recipient_email']
        amount = float(request.form['amount'])
        description = request.form['description']

        recipient = User.query.filter_by(email=recipient_email).first()

        if not recipient:
            flash('Recipient not found.', 'danger')
            return redirect(url_for('payments'))

        if current_user.balance < amount:
            flash('Insufficient funds.', 'danger')
            return redirect(url_for('payments'))

        # Perform the transaction
        current_user.balance -= amount
        recipient.balance += amount

        transaction = Transaction(
            sender_id=current_user.id,
            receiver_id=recipient.id,
            amount=amount,
            description=description
        )

        db.session.add(transaction)
        db.session.commit()
        flash('Payment sent successfully!', 'success')
        return redirect(url_for('transactions'))

    return render_template('payments.html', user=current_user)

# Transactions Page (transactions.html)
@app.route('/transactions')
@login_required
def transactions():
    sent_transactions = Transaction.query.filter_by(sender_id=current_user.id).all()
    received_transactions = Transaction.query.filter_by(receiver_id=current_user.id).all()
    return render_template('transactions.html', sent_transactions=sent_transactions, received_transactions=received_transactions)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():  # Add this context
        db.create_all()
    app.run(debug=True)