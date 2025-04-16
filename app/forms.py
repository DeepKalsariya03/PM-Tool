"""
Defines Flask-WTF form classes 
for user login and registration, 
for task and project creation using input fields with validation.
"""

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, EqualTo, Length, Optional

# Login form for existing users
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Registration form for new users
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Role', choices=[('admin', 'Admin'), ('manager', 'Manager'), ('member', 'Team Member')])
    submit = SubmitField('Register')

# Project form for project creation
class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    deadline = DateField('Deadline', format='%Y-%m-%d')
    status = SelectField('Status', choices=[('Active', 'Active'), ('Completed', 'Completed'), ('On Hold', 'On Hold')])
    submit = SubmitField('Save')

# Task form for task creation
class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    due_date = DateField('Due Date', format='%Y-%m-%d')
    status = SelectField('Status', choices=[('To Do', 'To Do'), ('In Progress', 'In Progress'), ('Completed', 'Completed')])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    assignee_id = SelectField('Assign to', coerce=int)  # User selection for assignment
    submit = SubmitField('Save Task')

class TeamAssignmentForm(FlaskForm):
    members = SelectMultipleField('Assign Team Members', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Update Team')

class ProfileForm(RegistrationForm):
    # Reusing RegistrationForm, but adding email and name fields
    name = StringField('Name', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[Length(min=6), Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('password', message='Passwords must match'), Optional()
    ])
    
    submit = SubmitField('Update Profile')