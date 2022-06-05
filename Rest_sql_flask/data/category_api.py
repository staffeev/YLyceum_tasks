import flask
from flask import jsonify, request

from . import db_session
from .category import Category

blueprint = flask.Blueprint(
    'category_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/categories')
def get_categories():
    db_sess = db_session.create_session()
    categories = db_sess.query(Category).all()
    return jsonify({'categories': [cat.to_dict() for cat in categories]})


@blueprint.route('/api/categories/<int:category_id>', methods=['GET'])
def get_one_category(category_id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).get(category_id)
    if not category_id:
        return jsonify({'Error': 'Not found'})
    return jsonify({'categories': category.to_dict()})


@blueprint.route('/api/categories', methods=['POST'])
def create_category():
    if not request.json:
        return jsonify({'Error': 'Empty request'})
    elif 'name ' not in request.json:
        return jsonify({'Error': 'Bad request'})
    if type(request.json['name']) != str:
        return jsonify({'Error': 'Values are incorrect'})
    db_sess = db_session.create_session()
    category = Category(name=request.json['name'])
    db_sess.add(category)
    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    db_sess = db_session.create_session()
    category = db_sess.query(Category).get(category_id)
    if not category:
        return jsonify({'Error': 'Not found'})
    db_sess.delete(category)
    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/api/categories/<int:category_id>', methods=['PUT'])
def edit_category(category_id):
    if not request.json:
        return jsonify({'Error': 'Empty request'})
    if request.json.get('id', 0):
        return jsonify({'Error': 'ID cannot be changed'})
    db_sess = db_session.create_session()
    category = db_sess.query(Category).get(category_id)
    if not category:
        return jsonify({'Error': 'Not found'})
    name = request.json.get('name', category.name)
    if type(name) != str:
        return jsonify({'Error': 'Values are incorrect'})
    category.name = name
    db_sess.commit()
    return jsonify({'Success': 'OK'})
