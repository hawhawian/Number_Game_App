from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import random
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'number_game'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

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
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
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
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cur.fetchone()
            if user:
                error = '帳號已存在'
            else:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('login'))
            cur.close()
        except Exception as e:
            error = f'資料庫連線錯誤: {e}'
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
