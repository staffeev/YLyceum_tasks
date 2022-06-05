from flask_restful import reqparse

# Парсер для создания пользователя
user_parser = reqparse.RequestParser()
user_parser.add_argument('surname', required=True)
user_parser.add_argument('name', required=True)
user_parser.add_argument('age', required=True, type=int)
user_parser.add_argument('position', required=True)
user_parser.add_argument('speciality', required=True)
user_parser.add_argument('address', required=True)
user_parser.add_argument('email', required=True)
user_parser.add_argument('password', required=True)

# Парсер для изменения пользователя (параметры не являются обязательными)
user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument('surname')
user_put_parser.add_argument('name')
user_put_parser.add_argument('age', type=int)
user_put_parser.add_argument('position')
user_put_parser.add_argument('speciality')
user_put_parser.add_argument('address')
user_put_parser.add_argument('email')
user_put_parser.add_argument('password')

# Парсер для создания работы
job_parser = reqparse.RequestParser()
job_parser.add_argument('team_leader', required=True, type=int)
job_parser.add_argument('job', required=True)
job_parser.add_argument('collaborators')
job_parser.add_argument('work_size', required=True, type=int)
job_parser.add_argument('category', required=True, type=int)
job_parser.add_argument('is_finished', type=bool)

# Парсер для изменения работы
job_put_parser = reqparse.RequestParser()
job_put_parser.add_argument('team_leader', type=int)
job_put_parser.add_argument('job')
job_put_parser.add_argument('collaborators')
job_put_parser.add_argument('work_size', type=int)
job_put_parser.add_argument('category', type=int)
job_put_parser.add_argument('is_finished', type=bool)

# Парсер для категорий
cat_parser = reqparse.RequestParser()
cat_parser.add_argument('name', required=True)
