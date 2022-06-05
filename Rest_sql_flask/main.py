from flask import Flask, render_template, redirect, request, \
    make_response, session, abort
from flask import jsonify
from flask_restful import Api

from data.category import Category
from data.departments import Department
from forms.departments import DepartmentsForm
from forms.jobs import JobsForm
from forms.user import RegisterForm, LoginForm
from data import db_session, jobs_api, users_api, category_api
from data.users import User
from data.jobs import Jobs
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user
from resources import users_resources, jobs_resources, category_resources
import datetime
from data import users_api


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
api = Api(app)
api.add_resource(users_resources.UsersListResource, '/api/v2/users')
api.add_resource(users_resources.UsersResource, '/api/v2/users/<int:user_id>')
api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs')
api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:job_id>')
api.add_resource(category_resources.CategoryListResource, '/api/v2/categories')
api.add_resource(category_resources.CategoryResource, '/api/v2/categories/<int:cat_id>')
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    jobs = db_sess.query(Jobs).all()
    categories = [', '.join([str(j.id) for j in i.categories]) for i in jobs]
    leaders_id = [i.team_leader for i in jobs]
    leaders = {i.id: f'{i.surname} {i.name}' for i in db_sess.query(
        User).filter(User.id.in_([job.team_leader for job in jobs]))}
    to_render = [leaders.get(i, 1) for i in leaders_id]
    return render_template("index.html", jobs=jobs, leaders=to_render,
                           categories=categories)


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


@app.route('/success')
def success():
    return '<p style="text-align: center;">Добро пожаловать!</p>'


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
            address=form.address.data,
            city_from=form.city.data
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
        job.categories.append(db_sess.query(Category).get(form.category.data))
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
            form.category.data = job.categories[0].id
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
            job.categories.remove(db_sess.query(Category).get(job.categories[0].id))
            job.categories.append(db_sess.query(Category).get(form.category.data))
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


@app.route('/users_show/<int:user_id>')
def show_user_city(user_id):
    v = users_api.get_city(user_id).json
    if v.get('surname', 0):
        return render_template('users_show.html',
                               data=users_api.get_city(user_id).json,
                               title='Hometown')
    return make_response("<h2>Error: Not found</h2>", 404)


@app.route("/departments")
def get_departments():
    departments = db_sess.query(Department).all()
    leaders_id = [i.chief for i in departments]
    leaders = {i.id: f'{i.surname} {i.name}' for i in db_sess.query(
        User).filter(User.id.in_([dep.chief for dep in departments]))}
    to_render = [leaders.get(i, 1) for i in leaders_id]
    return render_template("departments.html", departments=departments,
                           leaders=to_render)


@app.route('/adddep',  methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentsForm()
    if form.validate_on_submit():
        dep = Department()
        dep.title = form.title.data
        dep.chief = form.chief.data
        dep.members = form.members.data
        dep.email = form.email.data
        db_sess.add(dep)
        db_sess.commit()
        return redirect('/departments')
    return render_template('add_dep.html', title='Adding a Department',
                           form=form)


@app.route('/departments_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def department_delete(id):
    dep = db_sess.query(Department).filter(Department.id == id).filter(
        (Department.user == current_user) | (current_user.id == 1)).first()
    if dep:
        db_sess.delete(dep)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')


@app.route('/departments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    form = DepartmentsForm()
    if request.method == "GET":
        dep = db_sess.query(Department).filter(Department.id == id).filter(
            (Department.user == current_user) | (current_user.id == 1)).first()
        if dep:
            form.title.data = dep.title
            form.chief.data = dep.chief
            form.members.data = dep.members
            form.email.data = dep.email
        else:
            abort(404)
    if form.validate_on_submit():
        dep = db_sess.query(Department).filter(Department.id == id).filter(
            (Department.user == current_user) | (current_user.id == 1)).first()
        if dep:
            dep.title = form.title.data
            dep.chief = form.chief.data
            dep.members = form.members.data
            dep.email = form.email.data
            db_sess.commit()
            return redirect('/departments')
        else:
            abort(404)
    return render_template('add_dep.html', title='Edit Department', form=form)


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    db_sess = db_session.create_session()
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(category_api.blueprint)
    app.run(port=8080, host='127.0.0.1')