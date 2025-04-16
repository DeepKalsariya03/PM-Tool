"""
Handles CRUD operations for Projects:
- View, Create, Edit, and Delete projects
- Access controlled by user role (Admin or assigned Manager)
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Task, Project
from app.forms import ProjectForm, TaskForm, TeamAssignmentForm
from app.models import User

project = Blueprint('project', __name__)

# View all projects
from datetime import datetime, timedelta

# View all projects
@project.route('/projects', methods=['GET'])
@login_required
def view_projects():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    deadline_filter = request.args.get('deadline', '')

    projects = Project.query

    if search:
        projects = projects.filter(Project.name.ilike(f'%{search}%'))

    if status_filter:
        projects = projects.filter(Project.status == status_filter)

    # Filter by deadline
    if deadline_filter:
        today = datetime.today()
        
        if deadline_filter == 'this_week':
            start_date = today - timedelta(days=today.weekday())  # Start of the current week
            end_date = start_date + timedelta(days=7)  # End of the current week
            projects = projects.filter(Project.deadline >= start_date, Project.deadline <= end_date)
        
        elif deadline_filter == 'this_month':
            start_date = today.replace(day=1)  # Start of the current month
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)  # Start of next month
            projects = projects.filter(Project.deadline >= start_date, Project.deadline < end_date)
        
        elif deadline_filter == '1_year':
            end_date = today + timedelta(days=365)  # 1 year from today
            projects = projects.filter(Project.deadline <= end_date)

    # Calculate ongoing and completed project counts
    ongoing_count = Project.query.filter_by(status='Active').count()
    completed_count = Project.query.filter_by(status='Completed').count()

    # Calculate task progress for each project
    for project in projects:
        tasks = Task.query.filter_by(project_id=project.id).all()
        completed_tasks = [task for task in tasks if task.status == 'Completed']
        project.task_progress = (len(completed_tasks) / len(tasks)) * 100 if tasks else 0

    return render_template('projects/view_projects.html', projects=projects, ongoing_count=ongoing_count, completed_count=completed_count)



# View project details
@project.route('/projects/<int:project_id>/detail', methods=['GET', 'POST'])
@login_required
def view_project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project.id).all()
    completed_tasks = [task for task in tasks if task.status == 'Completed']

    form = TaskForm()
 
    form.assignee_id.choices = [(user.id, user.username) for user in User.query.filter_by(role='member').all()]

    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status=form.status.data,
            priority=form.priority.data,
            assignee_id=form.assignee_id.data,
            project_id=project.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('project.view_project_detail', project_id=project.id))

    # Get all assignees from tasks 
    assigned_user_ids = set(task.assignee_id for task in tasks if task.assignee_id)
    team_members = User.query.filter(User.id.in_(assigned_user_ids)).all()

    return render_template(
        'projects/project_detail.html',
        project=project,
        tasks=tasks,
        completed_tasks_count=len(completed_tasks),
        form=form,
        team_members=team_members
    )



# Create a new project
@project.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if current_user.role not in ['admin', 'manager']:
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            deadline=form.deadline.data,
            status=form.status.data,
            manager_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('project.view_projects'))

    return render_template('projects/create_project.html', form=form)

# Edit project
@project.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)

    # Only Admin or assigned manager can edit
    if current_user.role != 'admin' and current_user.role != 'manager' and current_user.id != project.manager_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('project.view_projects'))

    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        project.name = form.name.data
        project.description = form.description.data
        project.deadline = form.deadline.data
        project.status = form.status.data
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('project.view_projects'))

    return render_template('projects/edit_project.html', form=form, project=project)


# Delete project
@project.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)

    if current_user.role != 'Admin' and current_user.id != project.manager_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('project.view_projects'))

    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'info')
    return redirect(url_for('project.view_projects'))


# ---- Tasks ---

# Route for Task Creation
@project.route('/projects/<int:project_id>/task/create', methods=['POST'])
@login_required
def create_task(project_id):
    if current_user.role not in ['admin', 'project_manager']:
        flash('You do not have permission to create tasks.', 'danger')
        return redirect(url_for('project.view_project_detail', project_id=project_id))

    project = Project.query.get_or_404(project_id)
    title = request.form['title']
    description = request.form['description']
    assigned_to_id = request.form['assigned_to']
    deadline = request.form['deadline']

    assigned_to = User.query.get_or_404(assigned_to_id)
    task = Task(
        title=title,
        description=description,
        status='Pending',
        assigned_to=assigned_to,
        deadline=deadline,
        project_id=project.id
    )
    db.session.add(task)
    db.session.commit()

    flash('Task created successfully!', 'success')
    return redirect(url_for('project.view_project_detail', project_id=project.id))

# Route for Task Editing
@project.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if current_user.role not in ['admin', 'project_manager'] or task.assigned_to != current_user:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('project.view_project_detail', project_id=project.id))

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.assigned_to_id = request.form['assigned_to']
        task.deadline = request.form['deadline']
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('project.view_project_detail', project_id=project.id))

    # GET request
    users = User.query.all()
    return render_template('tasks/edit_task.html', task=task, project=project, users=users)

# Route for Task Deletion
@project.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if current_user.role not in ['admin', 'project_manager'] or task.assigned_to != current_user:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('project.view_project_detail', project_id=project.id))

    db.session.delete(task)
    db.session.commit()

    flash('Task deleted successfully!', 'success')
    return redirect(url_for('project.view_project_detail', project_id=project.id))