from flask import Flask, render_template, redirect, url_for, request, \
    make_response, session, abort
from flask import jsonify
from flask_restful import Api
from forms.jobs import JobsForm
from forms.loginform import LoadForm
from forms.user import RegisterForm, LoginForm
import json
from os import listdir
from os.path import join
from data import db_session, jobs_api
from data.users import User
from data.jobs import Jobs
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user
from resources import users_resources
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
api = Api(app)
api.add_resource(users_resources.UsersListResource, '/api/v2/users')
api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')
login_manager = LoginManager()
login_manager.init_app(app)


TEST_DATA = {'title': 'Анкета', 'surname': 'Watny', 'name': 'Mark',
             'education': 'выше среднего', 'profession': 'штурман марсохода',
             'sex': 'male', 'motivation': 'Всегда мечтал застрять на Марсе!)',
             'ready': True}

TEST_NAMES = ['Лунтик', 'Кузя', 'Пчеленок', 'Мила', 'Вупсень', 'Пупсень',
              'Баба Капа', 'Деда Шер']


@app.route("/")
def index():
    jobs = db_sess.query(Jobs).all()
    leaders_id = [i.team_leader for i in jobs]
    leaders = {i.id: f'{i.surname} {i.name}' for i in db_sess.query(
        User).filter(User.id.in_([job.team_leader for job in jobs]))}
    to_render = [leaders.get(i, 1) for i in leaders_id]
    return render_template("index.html", jobs=jobs, leaders=to_render)


@app.route('/<title>')
@app.route('/index/<title>')
def start(title):
    return render_template('base.html', title=title)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/list_prof/<f_list>')
def professions(f_list):
    return render_template('professions.html', param=f_list)


@app.route('/answer')
@app.route('/auto_answer')
def get_answers():
    return render_template('auto_answer.html', **TEST_DATA)


@app.route('/training/<prof>')
def simulators(prof):
    return render_template('training.html', prof=prof)


@app.route('/distribution')
def distribution():
    return render_template('distribution.html', name_list=TEST_NAMES)


@app.route('/table/<sex>/<int:age>')
def get_cabin(sex, age):
    return render_template('cabins.html', sex=sex, age=age)


@app.route('/success')
def success():
    return '<p style="text-align: center;">Добро пожаловать!</p>'


@app.route('/member')
def crew_member():
    return render_template('members.html',
                           data=json.load(open('templates/crew.json',
                                               encoding='utf8')))


@app.route('/gallery', methods=['GET', 'POST'])
def gallery():
    files = [url_for('static', filename=f'img/mars_pictures/{pic}') for pic in
             listdir('static/img/mars_pictures')]
    form = LoadForm()
    if form.validate_on_submit() and form.image.data:
        image_data = request.files[form.image.name]
        name = join('static/img/mars_pictures', image_data.filename)
        open(name, 'wb').write(image_data.read())
        files.append(name)
    return render_template('gallery.html', title='Красная планета',
                           data=files, form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            speciality=form.speciality.data,
            position=form.position.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(
            User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Wrong login or password",
                               form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addjob',  methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobsForm()
    if form.validate_on_submit():
        job = Jobs()
        job.job = form.title.data
        job.team_leader = form.team_leader.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        user = db_sess.query(User).filter(User.id == job.team_leader).first()
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Adding a Job',
                           form=form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    form = JobsForm()
    if request.method == "GET":
        job = db_sess.query(Jobs).filter(Jobs.id == id).filter(
            (Jobs.user == current_user) | (current_user.id == 1)).first()
        if job:
            form.title.data = job.job
            form.team_leader.data = job.team_leader
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        job = db_sess.query(Jobs).filter(Jobs.id == id).filter(
            (Jobs.user == current_user) | (current_user.id == 1)).first()
        if job:
            job.job = form.title.data
            job.team_leader = form.team_leader.data
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html', title='Edit Job', form=form)


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    job = db_sess.query(Jobs).filter(Jobs.id == id).filter(
        (Jobs.user == current_user) | (current_user.id == 1)).first()
    if job:
        db_sess.delete(job)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not found'}), 404)


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    db_sess = db_session.create_session()
    app.register_blueprint(jobs_api.blueprint)
    app.run(port=8080, host='127.0.0.1')