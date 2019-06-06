"""Routes controlling updating existing solutions"""

from flask import Blueprint, flash, render_template
from flask_login import login_required
from app import db
from app.forms import FileUpdateForm
from app.models import Language, Problem

update_bp = Blueprint('update_bp', __name__)

@update_bp.route('/update_solution', methods=['GET', 'POST'])
@login_required
def update_solution():
    """Route controlling updating existing solutions"""

    # dynamically load allowed file extensions
    file_update_form = FileUpdateForm()
    for extension in db.session.query(Language.extension).all():
        file_update_form.allowed_extensions.append(extension[0])

    if file_update_form.validate_on_submit():

        problem_id = file_update_form.data.get('problem_selection')
        problem_to_update = Problem.query.filter_by(problem_id=problem_id).first()

        # check problem_id exists
        if problem_to_update is None:
            flash("Solution does not exist - please try again", "warning")
        else:
            title = file_update_form.data.get('problem_title')
            contents = file_update_form.file_update.data.read()
            contents = contents.decode('utf-8').replace('\r\n', '\n')

            # check content is not null
            if not contents:
                flash("File must not be empty", "warning")

            else:
                extension = file_update_form.file_update.data.filename.split('.')[-1]
                language = Language.query.filter_by(extension=extension).first()
                language_id = language.language_id
                problem_to_update.contents = contents
                problem_to_update.language_id = language_id
                if title:
                    problem_to_update.title = title
                db.session.commit()
                flash("Solution updated", "success")

    return render_template('update_solution.html', file_update_form=file_update_form)
