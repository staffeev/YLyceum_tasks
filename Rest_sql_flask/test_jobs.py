from requests import get, delete, post, put
from data import db_session
from data.jobs import Jobs


# Получим все работы
print(get('http://127.0.0.1:8080/api/v2/jobs').json())
print()
# Получим одну работу
print(get('http://127.0.0.1:8080/api/v2/jobs/2').json())
print()
# Получим несуществующую работу -> {'message': 'Job 1000000000 not found'}
print(get('http://127.0.0.1:8080/api/v2/jobs/1000000000').json())
print()
# Некорректный параметр id работы -> {'Error': 'Not found'}
print(get('http://127.0.0.1:8080/api/v2/jobs/number').json())
print()
# Попробуем добавить работу
# Обязательные параметры - team_leader, work_size и job
# Если не передать обязательные параметры -> {'message': {'team_leader': 'Missing required parameter in the JSON body or the post body or the query string'}}
print(post('http://127.0.0.1:8080/api/v2/jobs').json())
print()
# Если передать не все обязательные параметры -> аналогично предыдущему примеру
print(post('http://127.0.0.1:8080/api/v2/jobs', json={'team_leader': 4}).json())
print()
# Если передать параметры неверного формата данных -> {'message': {'team_leader': "invalid literal for int() with base 10: 'number'"}}
print(post('http://127.0.0.1:8080/api/v2/jobs',
           json={'team_leader': 'number', 'work_size': 15,
                 'job': 'Test job do not complete'}).json())
print()
# Все параметры верны -> {'success': 'OK'}
print(post('http://127.0.0.1:8080/api/v2/jobs',
           json={'team_leader': 4, 'work_size': 15,
                 'job': 'Test job do not complete', 'is_finished': True,
                 'collaborators': '2, 3'}).json())
print()
# Проверим, что работа создалась
db_session.global_init('db/blogs.db')
db_sess = db_session.create_session()
job = db_sess.query(Jobs).all()[-1].id
print(get(f'http://127.0.0.1:8080/api/v2/jobs/{job}').json())
print()
# Изменим работу
print(put(f'http://127.0.0.1:8080/api/v2/jobs/{job}', json={'work_size': 99}).json())
print()
# Проверим изменения
print(get(f'http://127.0.0.1:8080/api/v2/jobs/{job}').json())
print()
# Удалим работу
print(delete(f'http://127.0.0.1:8080/api/v2/jobs/{job}').json())
print()
# Убедимся, что работа удалена -> {'message': 'Job 6 not found'}
print(get(f'http://127.0.0.1:8080/api/v2/jobs/{job}').json())