from flask import Flask, render_template, session, request, redirect
from config import Config
from base import init_db,get_db
app = Flask(__name__)
app.secret_key =Config.SECRET_KEY
init_db()
questions_free= [
    {"q":"2+2 =?",'a':'4'},
    {"q":"столица России?",'a':'Москва'},
    {"q":"110 - 17 =?",'a':'93'},
    {"q":"столица Франции?",'a':'париж'},
    {"q":"сколько дней в неделе?",'a':'7'},
    {"q":"спутник земли",'a':'луна'},
    {"q":"сколько месяцев в году",'a':'12'},
    {"q":"замершая вода это -?",'a':'лед'},
    {"q":"ближайшая к нам звезда?",'a':'солнце'},
    {"q":"сколько минут в одном часе",'a':'60'}
]
questions_pro = questions_free+[
    {"q":"сколько пальцев на руках у здорового человека ?",'a':'10'},
    {"q":"орган с помощью которого мы дышим?",'a':'легкие'},
    {"q":"110 - 17 =?",'a':'93'},
    {"q":"12 * 12=?",'a':'144'},
    {"q":"какой самый большой океан?",'a':'тихий'}
]
def get_questions(tier): #функция для выбора нужных типов вопросов
    if tier=="pro":
        return questions_pro
    else:
        return questions_free
def get_recomendat(percent): #выберает рекомендации после завершения теста
    if percent>=80:
        return "хорошо","у вас все хорошо"
    elif percent >=60:
        return "нормально","нормально, но есть риск"
    else:
        return "плохо","рекомендуется пройти на обследование к врачу"
@app.route('/')
def index():#показывает главную страницу
    return render_template('index.html',page='start')
@app.route('/start/<tier>')
def start(tier):#возобнавляет все к началу перед тестом
    session['tier']=tier
    session['score']=0
    session['current']=0
    return redirect('/question')
@app.route('/question')
def question():#показывает вопросы и проверяет их наличие
    tier=session.get('tier','free')
    questions=get_questions(tier)
    current=session.get('current',0)
    if session['current'] >=len(questions):
        return redirect('/result')
    q =questions[session['current']]
    return render_template('index.html',page='question',
                           question = q,current =session['current'],
                           total=len(questions))
@app.route('/answer',methods=['POST'])
def answer():#проверяет ответы, начисляет балы и дает переход на новый вопрос
    tier = session.get('tier', 'free')
    questions = get_questions(tier)
    current = session.get('current', 0)
    us_answer = request.form.get('answer','').lower().strip()
    correct =questions[session['current']]['a'].lower()
    if us_answer == correct:
        session['score']+=1
    session['current']+=1
    return redirect('/question')
@app.route("/result")
def result():#подсчитывает результаты и показывает их в бд
    tier = session.get('tier', 'free')
    questions = get_questions(tier)
    current = session.get('current', 0)
    score =session.get('score',0)
    total =len(questions)
    percent =int((score/total)*100) if total else 0
    estimation,text =get_recomendat(percent)
    conn=get_db()
    conn.cursor().execute('''INSERT INTO results (score,total,percent,risk,tier)
                             VALUES(?,?,?,?,?)''',
                          (score,total,percent,estimation,tier))
    conn.commit()
    conn.close()
    return render_template('index.html',page='result',
                           score=score,total=total,percent=percent,text=text,estimation=estimation,tier=tier)
if __name__ =="__main__":
    app.run(debug = True,port=5000)
