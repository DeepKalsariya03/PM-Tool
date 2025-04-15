"""
Handles CRUD operations for Projects:
- View, Create, Edit, and Delete projects
- Access controlled by user role (Admin or assigned Manager)
"""


from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Task, Project
from app.forms import TaskForm
from app.forms import ProjectForm

project = Blueprint('project', __name__)

# View all projects
@project.route('/projects')
@login_required
def view_projects():
    projects = Project.query.all()
    return render_template('projects/view_projects.html', projects=projects)

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
@project.route('/projects/<int:project_id>/tasks', methods=['GET'])
@login_required
def view_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project.id).all()
    return render_template('projects/view_tasks.html', project=project, tasks=tasks)

@project.route('/projects/<int:project_id>/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    if current_user.role not in ['admin', 'manager']:
        flash('Permission denied.', 'danger')
        return redirect(url_for('project.view_projects'))

    form = TaskForm()
    form.assignee_id.choices = [(user.id, user.username) for user in User.query.all()]  # Populate user list for assignment

    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status=form.status.data,
            priority=form.priority.data,
            assignee_id=form.assignee_id.data,
            project_id=project.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('project.view_tasks', project_id=project.id))

    return render_template('projects/create_task.html', form=form, project=project)

@project.route('/projects/<int:project_id>/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(project_id, task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role not in ['Admin', 'Project Manager'] and current_user.id != task.assignee_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('project.view_tasks', project_id=project_id))

    form = TaskForm(obj=task)
    form.assignee_id.choices = [(user.id, user.username) for user in User.query.all()]  # Populate user list for assignment

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        task.priority = form.priority.data
        task.assignee_id = form.assignee_id.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('project.view_tasks', project_id=project.id))

    return render_template('tasks/edit_task.html', form=form, project=project, task=task)

@project.route('/projects/<int:project_id>/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(project_id, task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.role not in ['Admin', 'Project Manager'] and current_user.id != task.assignee_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('project.view_tasks', project_id=project_id))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('project.view_tasks', project_id=project_id))
