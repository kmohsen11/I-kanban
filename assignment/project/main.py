from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from flask_login import login_required, current_user
from .models import Task
from .forms import TaskForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)
@main.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    form = TaskForm()  # Create an instance of the form

    # Check if the form has been submitted and validated
    if form.validate_on_submit():
        # Create a new Task and save it to the database
        new_task = Task(title=form.title.data, user_id=current_user.id, status=form.status.data)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully.')
        return redirect(url_for('main.tasks'))

    # Retrieve all tasks related to the current user
    all_tasks = Task.query.filter_by(user_id=current_user.id).all()

    # Prepare a list of potential parent tasks
    all_other_tasks = [task for task in all_tasks if task.parent is None]  #'None' means no parent task

    # Categorize tasks by status
    tasks_by_category = {
        'Todo': [task for task in all_tasks if task.status == 'todo' and task.parent_id is None],
        'Done': [task for task in all_tasks if task.status == 'done' and task.parent_id is None],
        'In Progress': [task for task in all_tasks if task.status == 'in-progress' and task.parent_id is None],
    }

    # Render the page with the necessary context
    return render_template(
        'tasks.html', # Template file
        form=form,
        all_tasks=all_tasks,  # Pass all tasks to the template
        all_other_tasks=all_other_tasks,
        tasks_by_category=tasks_by_category  # Pass tasks categorized by status to the template
    )

@main.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('main.tasks'))

    form = TaskForm(obj=task)  # Initialize the form with task data
    if form.validate_on_submit():
        form.populate_obj(task)  # Update task data from the form
        db.session.commit()
        flash('Task updated successfully', 'success')
        return redirect(url_for('main.tasks'))

    return render_template('edit_task.html', task=task, form=form)

@main.route('/add_subtask/<int:parent_id>', methods=['GET', 'POST'])
@login_required
def add_subtask(parent_id):
    form = TaskForm()
    parent_task = Task.query.get_or_404(parent_id)
    
    if form.validate_on_submit():
        title = form.title.data
        
        # Create a new subtask associated with the parent task
        subtask = Task(title=title, parent=parent_task, user=current_user)
        db.session.add(subtask)
        db.session.commit()
        
        flash('Subtask added!', 'success')
        return redirect(url_for('main.tasks'))
    
    return render_template('add_subtask.html', form=form, parent_task=parent_task)


@main.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    print(task_id)
    task = Task.query.get_or_404(task_id)
    print(task, task.title, task.user_id)

    # Check if the task belongs to the current user
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully.')
    else:
        flash('You do not have permission to delete this task.')

    return redirect(url_for('main.tasks'))


@main.route('/edit_subtask/<int:subtask_id>', methods=['GET', 'POST'])
@login_required
def edit_subtask(subtask_id):
    subtask = Task.query.get_or_404(subtask_id)
    form = TaskForm()

    if form.validate_on_submit():
        subtask.title = form.title.data
        db.session.commit()
        flash('Subtask updated successfully.', 'success')
        return redirect(url_for('main.tasks'))

    form.title.data = subtask.title
    return render_template('edit_subtask.html', subtask=subtask, form=form)


# Delete Subtask Route
@main.route('/delete_subtask/<int:subtask_id>', methods=['GET', 'POST'])
@login_required
def delete_subtask(subtask_id):
    subtask = Task.query.get_or_404(subtask_id)

    if request.method == 'POST':
        db.session.delete(subtask)
        db.session.commit()
        flash('Subtask deleted successfully.', 'success')
        return redirect(url_for('main.tasks'))
    
    return render_template('delete_subtask.html', subtask=subtask)

from flask import redirect, url_for, flash

@main.route('/reassign_task/<int:task_id>', methods=['POST'])
def reassign_task(task_id):
    # Get the task to be reassigned
    task = Task.query.get_or_404(task_id)
    
    # Get the new parent task or subtask ID from the form
    new_parent_id = request.form.get('new_parent_id')
    
    if new_parent_id:
        # Update the parent task or subtask ID for the task
        task.parent_id = new_parent_id
        
        # Save the changes to the database
        db.session.commit()
        
        flash('Task reassigned successfully', 'success')
    else:
        flash('Please select a new parent', 'error')
    
    return redirect(url_for('main.tasks'))

@main.route('/reassign_subtask/<int:subtask_id>', methods=['POST'])
@login_required
def reassign_subtask(subtask_id):
    subtask = Task.query.get(subtask_id)
    new_parent_id = request.form.get('new_parent_id')  # Get the new parent task or subtask ID from the form

    if subtask and new_parent_id:
        try:
            # Check if the new parent task exists among all tasks
            all_other_tasks = Task.query.filter(Task.id != subtask_id).all()  # Retrieve all tasks except the current one
            new_parent_task = next((t for t in all_other_tasks if t.id == int(new_parent_id)), None)

            if new_parent_task:
                subtask.parent_id = new_parent_task.id  # reassign the parent
                db.session.commit()
                flash('Subtask reassigned successfully.', 'success')
            else:
                flash('New parent task not found.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
    else:
        flash('Subtask or new parent ID not provided.', 'error')

    return redirect(url_for('main.tasks'))
