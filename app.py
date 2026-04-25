from flask import Flask, render_template, session, request, redirect
from config import Config
from base import init_db, get_db
import hashlib
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
init_db()
questions_free = [
    {"q": "2+2 =?", "a": "4"},
    {"q": "столица России?", "a": "москва"},
    {"q": "110 - 17 =?", "a": "93"},
    {"q": "столица Франции?", "a": "париж"},
    {"q": "сколько дней в неделе?", "a": "7"},
    {"q": "спутник земли", "a": "луна"},
    {"q": "сколько месяцев в году", "a": "12"},
    {"q": "замершая вода это -?", "a": "лед"},
    {"q": "ближайшая к нам звезда?", "a": "солнце"},
    {"q": "сколько минут в одном часе", "a": "60"}
]
questions_pro = questions_free + [
    {"q": "сколько пальцев на руках?", "a": "10"},
    {"q": "орган для дыхания?", "a": "легкие"},
    {"q": "12 * 12=?", "a": "144"},
    {"q": "самый большой океан?", "a": "тихий"},
    {"q": "сколько ног у паука?", "a": "8"}
]
def get_questions(tier):
    return questions_pro if tier == "pro" else questions_free
def get_recomendat(percent):
    if percent >= 80:
        return "хорошо", "у вас все хорошо"
    elif percent >= 60:
        return "нормально", "нормально, но есть риск"
    else:
        return "плохо", "рекомендуется пройти обследование"
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html', page='start')
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        fio = request.form.get('fio')
        otchestvo = request.form.get('otchestvo')
        phone = request.form.get('phone')
        city = request.form.get('city')
        consent = request.form.get('consent')
        if not username:
            error = 'имя обязательно'
        elif not password:
            error = 'пароль обязателен!'
        elif not fio:
            error = 'ФИО обязательно!'
        elif not otchestvo:
            error = 'Отчество обязательно!'
        elif not phone:
            error = 'телефон обязателен!'
        elif not city:
            error = 'город обязателен!'
        elif not consent:
            error = 'согласие обязательно!'
        else:
            pswd_hash = hashlib.sha256(password.encode()).hexdigest()
            conn = get_db()
            c = conn.cursor()
            try:
                c.execute('''INSERT INTO users (username, password, fio, otchestvo, phone, city, consent) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (username, pswd_hash, fio, otchestvo, phone, city, 1))
                conn.commit()
                session['user_id'] = c.lastrowid
                session['username'] = username
                session['fio'] = fio
                session['otchestvo'] = otchestvo
                session['city'] = city
                conn.close()
                print(f'Пользователь {username} зарегистрирован!')
                return redirect('/login')
            except Exception as e:
                print(f'ОШИБКА: {e}')
                error = f'имя занято ({e})'
                conn.close()
        return render_template('auth.html', page='register', error=error)
    return render_template('auth.html', page='register', error=error)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                  (username, pwd_hash))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['fio'] = user['fio']
            session['otchestvo'] = user['otchestvo']
            session['city'] = user['city']
            return redirect('/')
        error = 'неверный логин или пароль'
    return render_template('auth.html', page='login', error=error)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/start/<tier>')
def start(tier):
    if 'user_id' not in session:
        return redirect('/login')
    session['tier'] = tier
    session['score'] = 0
    session['current'] = 0
    return redirect('/question')
@app.route('/question')
def question():
    if 'user_id' not in session:
        return redirect('/login')
    tier = session.get('tier', 'free')
    questions = get_questions(tier)
    current = session.get('current', 0)
    if current >= len(questions):
        return redirect('/result')
    q = questions[current]
    return render_template('index.html', page='question',
                           question=q, current=current,
                           total=len(questions), tier=tier)
@app.route('/answer', methods=['POST'])
def answer():
    if 'user_id' not in session:
        return redirect('/login')
    tier = session.get('tier', 'free')
    questions = get_questions(tier)
    current = session.get('current', 0)
    if current < len(questions):
        us_answer = request.form.get('answer', '').lower().strip()
        correct = questions[current]['a'].lower()
        if us_answer == correct:
            session['score'] += 1
        session['current'] += 1
    return redirect('/question')
@app.route("/result")
def result():
    if 'user_id' not in session:
        return redirect('/login')
    tier = session.get('tier', 'free')
    questions = get_questions(tier)
    score = session.get('score', 0)
    total = len(questions)
    percent = int((score / total) * 100) if total else 0
    estimation, text = get_recomendat(percent)
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO results (user_id, score, total, percent, risk, tier)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (session['user_id'], score, total, percent, estimation, tier))
    conn.commit()
    conn.close()
    return render_template('index.html', page='result',
                           score=score, total=total, percent=percent,
                           text=text, estimation=estimation, tier=tier)
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM results WHERE user_id = ? ORDER BY id DESC',
              (session['user_id'],))
    results = c.fetchall()
    conn.close()
    return render_template('profile.html', results=results)
if __name__ == "__main__":
    app.run(debug=True, port=5000)
