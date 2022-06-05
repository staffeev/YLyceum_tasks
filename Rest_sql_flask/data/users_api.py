import flask
from flask import jsonify, request
from geocoder import get_address_pos_and_spn
from . import db_session
from .users import User
import requests

blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [user.to_dict() for user in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_one_job(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'Error': 'Not found'})
    return jsonify({'users': user.to_dict()})


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    if not request.json:
        return jsonify({'Error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['surname', 'name', 'age', 'position', 'speciality',
                  'email', 'address', 'password']):
        return jsonify({'Error': 'Bad request'})

    data = ['surname', 'name', 'age', 'position', 'speciality', 'email',
            'address']
    attr = {i: request.json[i] for i in data}
    if any(type(x) != str for x in attr if x != 'age') or type(
            attr['age']) != int:
        return jsonify({'Error': 'Values are incorrect'})
    db_sess = db_session.create_session()
    user = User()
    for i in attr:
        setattr(user, i, attr[i])
    user.set_password(request.json['password'])
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'Error': 'Not found'})
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if not request.json:
        return jsonify({'Error': 'Empty request'})
    if request.json.get('id', 0):
        return jsonify({'Error': 'ID cannot be changed'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'Error': 'Not found'})

    data = ['surname', 'name', 'age', 'position', 'speciality', 'email',
            'address']
    new_attr = {i: request.json.get(i, user.__dict__[i]) for i in data}

    if any(type(x) != str for x in new_attr if x != 'age') or type(
            new_attr['age']) != int:
        return jsonify({'Error': 'Values are incorrect'})

    for i in new_attr:
        if i != 'password':
            setattr(user, i, new_attr[i])
        else:
            user.set_password(new_attr[i])

    db_sess.commit()
    return jsonify({'Success': 'OK'})


@blueprint.route('/users_show/<int:user_id>')
def get_city(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'Error': 'Not found'})
    res = get_address_pos_and_spn(user.city_from)
    if not res:
        return jsonify({'surname': user.surname, 'name': user.name,
                        'city': user.city_from, 'image': None})
    pos, spn = res
    response = requests.get('https://static-maps.yandex.ru/1.x/?',
                            params={'ll': ','.join(map(str, pos)),
                                    'l': 'sat', 'spn': spn})
    return jsonify({'surname': user.surname, 'name': user.name,
                    'city': user.city_from, 'image': response.url})
