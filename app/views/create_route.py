"""Routes controlling creation of new solutions"""

from flask import Blueprint, flash, render_template
from flask_login import login_required
from app import db
from app.forms import FileUploadForm
from app.models import Language, Problem

create_bp = Blueprint('create_bp', __name__)

@create_bp.route('/create_solution', methods=['GET', 'POST'])
@login_required
def create_solution():
    """Route controlling creation of new solutions"""

    # dynamically load allowed file extensions
    file_upload_form = FileUploadForm()
    for extension in db.session.query(Language.extension).all():
        file_upload_form.allowed_extensions.append(extension[0])

    if file_upload_form.is_submitted():
        if file_upload_form.validate():

            problem_id = file_upload_form.data.get('problem_selection')

            # check problem_id doesn't already exist
            if Problem.query.filter_by(problem_id=problem_id).first() is not None:
                flash("A solution for that problem already exists - please specify an unsolved "
                      "problem or update the solution", "warning")

            else:
                title = file_upload_form.data.get('problem_title')
                contents = file_upload_form.file_upload.data.read()
                contents = contents.decode('utf-8').replace('\r\n', '\n')

                # check content is not null
                if not contents:
                    flash("File must not be empty", "warning")

                else:
                    # create objects to add to database
                    extension = file_upload_form.file_upload.data.filename.split('.')[-1]
                    language = Language.query.filter_by(extension=extension).first()
                    language_id = language.language_id
                    problem = Problem(problem_id=problem_id, contents=contents,
                                      language_id=language_id, title=title)

                    # add objects to database
                    db.session.add(problem)
                    db.session.commit()

                    # clear form values
                    file_upload_form.problem_selection.raw_data = ['']
                    file_upload_form.problem_title.data = None

                    flash("Solution created", "success")

        else:
            error_messages = [f.process_errors[0] for f in file_upload_form._fields.values() if f.process_errors]
            if error_messages:
                flash(error_messages[0], "warning")
            else:
                flash("An error was encountered - please review inputs and try again", "warning")

    return render_template('create_solution.html', file_upload_form=file_upload_form)
