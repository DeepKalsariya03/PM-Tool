"""
Defines the SQLAlchemy models for User, Project and Task entities.
Includes password hashing and user-role support for authentication.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

# User model for storing registered users and roles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'manager', 'member'

    def set_password(self, password):
        # Hash the password before storing
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check password hash for login verification
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
# Project model for storing project details
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Active')  # Active, Completed, On Hold, etc.
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Assigned manager

    manager = db.relationship('User', backref='managed_projects')

# Task model for storing project details
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='To Do')  # e.g., 'To Do', 'In Progress', 'Completed'
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)  # Associated project
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Assigned user

    # Relationships
    project = db.relationship('Project', backref=db.backref('tasks', lazy=True))
    assignee = db.relationship('User', backref=db.backref('tasks_assigned', lazy=True))

    def __repr__(self):
        return f'<Task {self.title}>'


