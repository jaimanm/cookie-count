from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cookies.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
db = SQLAlchemy(app)

GLOBAL_PASSWORD = 'your_password'  # Change this to your desired password

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

with app.app_context():
    db.create_all()
    if not Counter.query.first():
        initial_counter = Counter(count=0)
        db.session.add(initial_counter)
        db.session.commit()

@app.route('/')
def index():
    counter = Counter.query.first()
    logs = Log.query.order_by(Log.timestamp.desc()).limit(5).all()
    return render_template('index.html', count=counter.count, logs=logs)

@app.route('/increment', methods=['GET', 'POST'])
def increment():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == GLOBAL_PASSWORD:
            counter = Counter.query.first()
            counter.count += 1
            log = Log(username=username)
            db.session.add(log)
            db.session.commit()
            flash('Cookie count incremented successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid password', 'error')
    return render_template('increment.html')

if __name__ == '__main__':
    app.run(debug=True)
