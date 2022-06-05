from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired


class DepartmentsForm(FlaskForm):
    title = StringField('Department Title', validators=[DataRequired()])
    chief = IntegerField('Chief Id', validators=[DataRequired()])
    members = StringField('Members')
    email = EmailField('Department Email')
    submit = SubmitField('Submit')