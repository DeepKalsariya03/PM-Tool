"""
Defines main app routes:
- Home page (public)
- Dashboard page (protected, shown after login)
"""

from app import db
from flask import Blueprint, render_template , redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Task
from werkzeug.security import generate_password_hash
from datetime import date, timedelta
from app.forms import ProfileForm

main = Blueprint('main', __name__)

# Home route
@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')

# Dashboard page shown after login
# User Dashboard Route (Profile Update)
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def user_dashboard():
    tasks = Task.query.filter_by(assignee_id=current_user.id).all()

    # Status summary
    status_counts = {
        'To Do': sum(1 for t in tasks if t.status == 'To Do'),
        'In Progress': sum(1 for t in tasks if t.status == 'In Progress'),
        'Completed': sum(1 for t in tasks if t.status == 'Completed'),
    }

    # Upcoming deadlines
    upcoming_tasks = [t for t in tasks if t.due_date and t.due_date >= date.today() and t.due_date <= date.today() + timedelta(days=7)]

    # Initialize the profile form
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Update user info
        current_user.name = form.name.data
        current_user.email = form.email.data

        # Only update password if a new one is provided
        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.user_dashboard'))

    return render_template(
        'dashboard.html', 
        tasks=tasks, 
        status_counts=status_counts, 
        upcoming_tasks=upcoming_tasks, 
        form=form
    )
