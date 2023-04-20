from flask import redirect, render_template, Flask
from flask_login import login_user, LoginManager, logout_user, login_required, current_user

from data_db import db_session
from data_db.answer import Answer
from data_db.question import Question
from data_db.users import User
from forms.LoginForm import LoginForm
from forms.QuestionForm import QuestionForm
from forms.RegisterForm import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwwqrwqrg44t5gfdgfd'
login_manager = LoginManager()
login_manager.init_app(app)
question_ids = []
users_data = {}


def generate_form(question_id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(
        Question.id == question_id).first()
    form = QuestionForm()
    if question.is_radio():
        del form.checkAnswers
        choices = []
        for answer in question.answers:
            choices.append((answer.id, answer.text))
        form.radioAnswers.choices = choices
    else:
        del form.radioAnswers
        choices = []
        for answer in question.answers:
            choices.append((answer.id, answer.text))
        form.checkAnswers.choices = choices

    return [form, question]


def read_question_ids():
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).order_by(Question.id).all()
    for question in questions:
        question_ids.append(question.id)
    pass


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def reset_user(user_id):
    del users_data[user_id]


@app.route("/", methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect("/login")

    if current_user.id not in users_data:
        users_data[current_user.id] = {'current_question_index': 0}

    [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])

    if form.validate_on_submit():
        if users_data[current_user.id]['current_question_index'] < (len(question_ids) - 1):
            users_data[current_user.id]['current_question_index'] += 1
            [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
        else:
            reset_user(current_user.id)
            return render_template("finish.html")
    else:
        print(form.errors)
    return render_template("index.html", question=question, form=form,
                           current_question_index=users_data[current_user.id]['current_question_index'] + 1,
                           total_questions=len(question_ids))

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    read_question_ids()
    app.run(port=8081, host='127.0.0.1')
