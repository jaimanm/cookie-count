from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cookies.db'
app.config['SECRET_KEY'] = 'minecraft'
db = SQLAlchemy(app)

CORS(app)

GLOBAL_PASSWORD = 'ftr'

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    previous_count = db.Column(db.Integer, nullable=False)
    new_count = db.Column(db.Integer, nullable=False)

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
            return render_template('increment.html', count=counter.count, authenticated=True, username=username)
        else:
            return render_template('increment.html', authenticated=False)
    return render_template('increment.html', authenticated=False)

@app.route('/update-count', methods=['POST'])
def update_count():
    new_count = request.form.get('count', type=int)
    username = request.form.get('username')
    
    if new_count is not None and username:
        counter = Counter.query.first()
        old_count = counter.count
        counter.count = new_count
        log = Log(
            username=username,
            previous_count=old_count,
            new_count=new_count
        )
        db.session.add(log)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/increment-count', methods=['POST'])
def increment_count():
    username = request.form.get('username')
    password = request.form.get('password')
    increment_by = request.form.get('increment_by', default=1, type=int)  # Default to 1 if not provided

    if password == GLOBAL_PASSWORD:
        counter = Counter.query.first()
        if counter:
            counter.count += increment_by  # Increment the count by the specified amount
            log = Log(
                username=username,
                previous_count=counter.count - increment_by,  # Previous count before increment
                new_count=counter.count
            )
            db.session.add(log)
            db.session.commit()
            return {'message': 'Count incremented successfully', 'new_count': counter.count}, 200
        else:
            return {'message': 'Counter not found'}, 404
    else:
        return {'message': 'Authentication failed'}, 403


if __name__ == '__main__':
    app.run(debug=True)
