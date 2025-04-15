"""
Defines main app routes:
- Home page (public)
- Dashboard page (protected, shown after login)
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

# Home route
@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')

# Dashboard page shown after login
@main.route('/dashboard')
@login_required
def dashboard():
    # Display a welcome message and user role
    return render_template('dashboard.html', user=current_user)


