from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    title = StringField('Task', validators=[DataRequired()], render_kw={"placeholder": "Enter your task"})
    status = SelectField('Status', choices=[('todo', 'To Do'), ('in-progress', 'In Progress'), ('done', 'Done')], default='todo', validators=[DataRequired()])
    submit = SubmitField('Submit')
