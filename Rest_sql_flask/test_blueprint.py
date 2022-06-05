from requests import post, put
from data import db_session
from data.jobs import Jobs
from data.category import Category

db_session.global_init('db/blogs.db')
session = db_session.create_session()
job = session.query(Jobs).filter(Jobs.id == 4).first()
category = session.query(Category).filter(Category.id == 2).first()
job.categories.append(category)
session.commit()