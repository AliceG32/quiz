
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
correct_answers_count = 0
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

    db_sess.close()
    return [form, question]


def count_correct_answers(form, question):
    result = 0
    if question.is_radio():
        for a in question.answers:
            if a.correct and a.id == form.radioAnswers.data:
                result += 1
                break
    else:
        # создание множества ответов из формы
        answers_from_form = set(map(int, form.checkAnswers.data))
        correct_answers = set()
        incorrect_answers = set()
        for a in question.answers:
            if a.correct:
                correct_answers.add(a.id)
            else:
                incorrect_answers.add(a.id)
        result = len(correct_answers.intersection(answers_from_form)) - len(
            incorrect_answers.intersection(answers_from_form))
    if result < 0:
        result = 0

    return result

# функция считывает все вопросы в массив и возвращает количеств корректных ответов
def read_question_ids():
    correct_answers_count_ = 0
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).order_by(Question.id).all()
    for question in questions:
        question_ids.append(question.id)
        for a in question.answers:
            if a.correct:
                correct_answers_count_ += 1
    db_sess.close()
    return correct_answers_count_


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
    # проверяет, что пользователь зашел первый раз
    if current_user.id not in users_data:
        users_data[current_user.id] = {'current_question_index': 0, 'correct_answers': 0}

    [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
    if form.validate_on_submit():
        [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
        users_data[current_user.id]['correct_answers'] += count_correct_answers(form, question)
        correct_answers = users_data[current_user.id]['correct_answers']
        # проверка последний ли вопрос
        # если не последний, то создается новая форма
        if users_data[current_user.id]['current_question_index'] < (len(question_ids) - 1):
            users_data[current_user.id]['current_question_index'] += 1
            [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
        else:
            reset_user(current_user.id)
            current_correct_answers = current_user.correct_answers
            current_total_correct_answers = current_user.total_correct_answers

            if current_total_correct_answers != 0:
                current_correct_percent = int((100 * current_correct_answers / current_total_correct_answers))
            else:
                current_correct_percent = 0

            if correct_answers_count != 0:
                correct_percent = int((100 * correct_answers / correct_answers_count))
            else:
                correct_percent = 0

            if correct_percent > current_correct_percent:
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == current_user.id).first()
                user.correct_answers = correct_answers
                user.total_correct_answers = correct_answers_count
                db_sess.commit()

            if correct_percent > current_correct_percent:
                current_correct_answers = correct_answers
                current_total_correct_answers = correct_answers_count
                current_correct_percent = correct_percent

            return render_template("finish.html", correct_count=correct_answers,
                                   correct_answers_count=correct_answers_count,
                                   correct_percent=correct_percent,
                                   current_total_correct_answers=current_total_correct_answers,
                                   current_correct_answers=current_correct_answers,
                                   current_correct_percent=current_correct_percent
                                   )

    return render_template("index.html", question=question, form=form,
                           current_question_index=users_data[current_user.id]['current_question_index'] + 1,
                           total_questions=len(question_ids))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


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
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    correct_answers_count = read_question_ids()
    app.run(port=8081, host='127.0.0.1')
