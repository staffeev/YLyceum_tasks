from requests import get, delete, post, put
from data import db_session
from data.users import User


# Получим всех пользователей
print(get('http://127.0.0.1:8080/api/v2/users').json())
print()
# Получим одного пользователя
print(get('http://127.0.0.1:8080/api/v2/users/1').json())
print()
# Получим несуществующего пользователя -> {'message': 'User 1000000000 not found'}
print(get('http://127.0.0.1:8080/api/v2/users/1000000000').json())
print()
# Некорректный параметр id пользователя -> {'Error': 'Not found'}
print(get('http://127.0.0.1:8080/api/v2/users/number').json())
print()
# Попробуем добавить пользователя
# Если не передать параметры -> {'message': {'surname': 'Missing required parameter in the JSON body or the post body or the query string'}}
print(post('http://127.0.0.1:8080/api/v2/users').json())
print()
# Если передать не все параметры -> аналогично предыдущему примеру
print(post('http://127.0.0.1:8080/api/v2/users', json={'surname': 'Kek',
                                                       'name': 'Andrew'}).json())
print()
# Если передать параметры неверного формата данных -> {'message': {'age': "invalid literal for int() with base 10: 'number'"}}
print(post('http://127.0.0.1:8080/api/v2/users',
           json={'surname': 'Kek', 'name': 'Andrew', 'age': 'number',
                 'position': 'captain',
                 'speciality': 'lord', 'address': 'module_0',
                 'email': 'iuifg',
                 'password': 'iyfgeefmhgf'}).json())
print()
# Все параметры верны -> {'success': 'OK'}
print(post('http://127.0.0.1:8080/api/v2/users',
           json={'surname': 'Kek', 'name': 'Andrew', 'age': 31,
                 'position': 'captain',
                 'speciality': 'lord', 'address': 'module_0',
                 'email': 'iuifg',
                 'password': 'iyfgeefmhgf'}).json())
print()
# Проверим, что пользователь создался
db_session.global_init('db/blogs.db')
db_sess = db_session.create_session()
user = db_sess.query(User).all()[-1].id
print(get(f'http://127.0.0.1:8080/api/v2/users/{user}').json())
print()
# Изменим данные пользователя
print(put(f'http://127.0.0.1:8080/api/v2/users/{user}', json={'age': 99}).json())
print()
# Проверим изменения
print(get(f'http://127.0.0.1:8080/api/v2/users/{user}').json())
print()
# Удалим пользователя
print(delete(f'http://127.0.0.1:8080/api/v2/users/{user}').json())
print()
# Убедимся, что пользователь удален -> {'message': 'User 5 not found'}
print(get(f'http://127.0.0.1:8080/api/v2/users/{user}').json())