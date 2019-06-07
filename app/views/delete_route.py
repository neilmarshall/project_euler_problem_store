from flask import Blueprint, flash, render_template
from flask_login import login_required
from app import db
from app.forms import FileDeleteForm
from app.models import Problem

delete_bp = Blueprint('delete_bp', __name__)

@delete_bp.route('/delete_solution', methods=['GET', 'POST'])
@login_required
def delete_solution():
    file_delete_form = FileDeleteForm()
    if file_delete_form.validate_on_submit():
        problem_id = file_delete_form.data.get('problem_selection')
        problem_to_delete = Problem.query.filter_by(problem_id=problem_id).first()
        if problem_to_delete is None:
            flash("Solution does not exist - please try again", "warning")
        else:
            db.session.delete(problem_to_delete)
            db.session.commit()
            flash("Solution deleted", "success")
    return render_template('delete_solution.html', file_delete_form=file_delete_form)
