from flask import jsonify
from flask_restful import Resource, abort
from data import db_session
from data.category import Category
from arg_parse import cat_parser


def abort_if_cat_not_found(cat_id):
    session = db_session.create_session()
    category = session.query(Category).get(cat_id)
    if not category:
        abort(404, message=f"Category {cat_id} not found")


class CategoryResource(Resource):
    def get(self, cat_id):
        abort_if_cat_not_found(cat_id)
        session = db_session.create_session()
        category = session.query(Category).get(cat_id)
        return jsonify({'category': category.to_dict()})

    def delete(self, cat_id):
        abort_if_cat_not_found(cat_id)
        session = db_session.create_session()
        category = session.query(Category).get(cat_id)
        session.delete(category)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, cat_id):
        abort_if_cat_not_found(cat_id)
        args = cat_parser.parse_args()
        session = db_session.create_session()
        category = session.query(Category).get(cat_id)
        setattr(category, 'name', args['name'])
        session.commit()
        return jsonify({'success': 'OK'})


class CategoryListResource(Resource):
    def get(self):
        session = db_session.create_session()
        categories = session.query(Category).all()
        return jsonify({'categories': [item.to_dict() for item in categories]})

    def post(self):
        args = cat_parser.parse_args()
        session = db_session.create_session()
        category = Category(name=args['name'])
        session.add(category)
        session.commit()
        return jsonify({'success': 'OK'})