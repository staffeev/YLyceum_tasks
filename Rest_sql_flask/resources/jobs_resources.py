from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.category import Category
from data.jobs import Jobs
from arg_parse import job_parser, job_put_parser


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'job': job.to_dict()})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, job_id):
        abort_if_job_not_found(job_id)
        args = job_put_parser.parse_args()
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        changed = {j: args[j] for j in job.__dict__ if args.get(
            j, None) is not None and j != 'categories'}
        for i in changed:
            setattr(job, i, changed[i])
        category = args.get('category', job.categories[0].id)
        job.categories.remove(session.query(Category).get(job.categories[0].id))
        job.categories.append(session.query(Category).get(category))
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict() for item in jobs]})

    def post(self):
        args = job_parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            collaborators=args['collaborators'],
            work_size=args['work_size'],
            is_finished=args['is_finished']
        )
        job.categories.append(session.query(Category).get(args['category']))
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})