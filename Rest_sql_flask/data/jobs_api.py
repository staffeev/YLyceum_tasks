import flask
from flask import jsonify, request

from . import db_session
from .category import Category
from .jobs import Jobs

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [job.to_dict() for job in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_one_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'Error': 'Not found'})
    return jsonify(
        {
            'jobs': job.to_dict()
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_job():
    if not request.json:
        return jsonify({'Error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'collaborators', 'work_size',
                  'is_finished', 'category']):
        return jsonify({'Error': 'Bad request'})
    team_leader = request.json['team_leader']
    caption = request.json['job']
    collaborators = request.json['collaborators']
    work_size = request.json['work_size']
    is_finished = request.json['is_finished']
    category = request.json['category']
    if type(collaborators) != str or type(is_finished) != bool or \
            type(team_leader) != int or type(work_size) != int or \
            type(caption) != str or type(category) != int:
        return jsonify({'Error': 'Values are incorrect'})
    db_sess = db_session.create_session()
    job = Jobs(
        team_leader=team_leader,
        job=caption,
        collaborators=collaborators,
        work_size=work_size,
        is_finished=is_finished
    )
    job.categories.append(db_sess.query(Category).get(category))
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'Error': 'Not found'})
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    if not request.json:
        return jsonify({'Error': 'Empty request'})
    if request.json.get('id', 0):
        return jsonify({'Error': 'ID cannot be changed'})
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'Error': 'Not found'})

    team_leader = request.json.get('team_leader', job.team_leader)
    caption = request.json.get('job', job.job)
    collaborators = request.json.get('collaborators', job.collaborators)
    work_size = request.json.get('work_size', job.work_size)
    category = request.json.get('category', job.categories[0].id)
    is_finished = request.json.get('is_finished', job.is_finished)

    if type(collaborators) != str or type(is_finished) != bool or \
        type(team_leader) != int or type(work_size) != int or \
            type(caption) != str or type(category) != int:
        return jsonify({'Error': 'Values are incorrect'})

    job.job = caption
    job.team_leader = team_leader
    job.work_size = team_leader
    job.collaborators = collaborators
    job.categories.remove(db_sess.query(Category).get(job.categories[0].id))
    job.categories.append(db_sess.query(Category).get(category))
    job.is_finished = is_finished
    db_sess.commit()
    return jsonify({'Success': 'OK'})
