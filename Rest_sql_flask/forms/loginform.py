from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    astronaut_id = StringField('id астронавта', validators=[DataRequired()])
    astronaut_password = PasswordField('Пароль астронавта',
                                       validators=[DataRequired()])
    captain_id = StringField('id капитана', validators=[DataRequired()])
    captain_password = PasswordField('Пароль капитана',
                                     validators=[DataRequired()])
    submit = SubmitField('Доступ')


class LoadForm(FlaskForm):
    image = FileField('Выбрать картинку', validators=[DataRequired()])
    submit = SubmitField('Отправить')