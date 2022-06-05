from requests import get, put

# Рассмотрим изначальные данные
print(get('http://127.0.0.1:8080/api/jobs/1').json())
print()
print()
# Параметры не переданы -> ошибка {'Error': 'Empty request'}
print(put('http://127.0.0.1:8080/api/jobs/1', json={}).json())
print()
# Попытка изменить id работы -> ошибка {'Error': 'ID cannot be changed'}
# (сделано на всякий случай, чтоб пользователь случайно не сломал БД)
print(put('http://127.0.0.1:8080/api/jobs/1', json={'id': 5}).json())
print()
# Переданы переметры неверного типа -> ошибка {'Error': 'Values are incorrect'}
print(put('http://127.0.0.1:8080/api/jobs/1', json={'is_finished': 24}).json())
print()
# Параметры переданы верно -> успех
print(put('http://127.0.0.1:8080/api/jobs/1',
          json={'is_finished': True, 'work_size': 80,
                'collaboratots': '5, 6, 10'}).json())
print()
print()
# Удостоверимся, что данные изменились
print(get('http://127.0.0.1:8080/api/jobs/5').json())