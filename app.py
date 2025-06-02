from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def index_html():
    return render_template('index.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('game'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            session['answer'] = random.randint(1, 100)
            session['tries'] = 0
            session['history'] = []
            return redirect(url_for('game'))
        else:
            error = '帳號或密碼錯誤'
    return render_template('login.html', error=error)

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            error = '帳號已存在'
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/game.html', methods=['GET', 'POST'])
def game():
    if 'username' not in session:
        return redirect(url_for('login'))
    message = None
    if 'history' not in session:
        session['history'] = []
    if request.method == 'POST':
        try:
            guess = int(request.form['guess'])
        except:
            guess = None
        answer = session.get('answer')
        session['tries'] += 1
        result = ''
        if guess == answer:
            message = f'恭喜你猜對了! 正解是{answer}，共猜了 {session["tries"]} 次，繼續輸入來繼續遊戲吧!'
            result = '答對'

            session['answer'] = random.randint(1, 100)
            session['tries'] = 0
            session['history'].append({'guess': guess, 'result': result})

            session['history'] = []
        elif guess is not None:
            if guess < answer:
                result = '太小'
                message = '數字太小！'
            else:
                result = '太大'
                message = '數字太大！'
            session['history'].append({'guess': guess, 'result': result})
    history = session.get('history', [])
    history = list(reversed(history))
    return render_template('game.html', username=session['username'], message=message, history=history)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/style/style.css')
def style_css():
    return send_from_directory('style', 'style.css')

@app.route('/img/number.png')
def number_png():
    return send_from_directory('img', 'number.png')

if __name__ == '__main__':
    app.run(debug=True)
