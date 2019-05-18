from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import db
from app.forms import FileDeleteForm, FileUpdateForm, FileUploadForm, LoginForm, ProblemSelectionForm
from app.models import Language, Problem, User

app_bp = Blueprint('app_bp', __name__)

@app_bp.route('/', methods=['GET', 'POST'])
def index():

    # check if routing has come via problem selection form
    problem_selection_form = ProblemSelectionForm()
    if problem_selection_form.validate_on_submit():
        new_page = r'/problem' + str(int(problem_selection_form.problem_selection.data))
        return redirect(new_page)

    # check if routing has come via login form
    login_form=LoginForm()  # note: test user has credentials ('test', 'pass')
    if login_form.validate_on_submit():
        username, password = login_form.data.get('username'), login_form.data.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Username not recognised or invalid password provided - please try again')
            return redirect(url_for('app_bp.index'))
        else:
            login_user(user)            

    # else have navigated directly to home page, or have been redirected
    page = request.args.get('page', 1, type=int)
    problem_solutions = Problem.query.order_by('problem_id').paginate(page=page, per_page=current_app.config['SOLUTIONS_TO_SHOW'])
    next_url = url_for('app_bp.index', page=problem_solutions.next_num) if problem_solutions.has_next else None
    prev_url = url_for('app_bp.index', page=problem_solutions.prev_num) if problem_solutions.has_prev else None
    while len(problem_solutions.items) < current_app.config['SOLUTIONS_TO_SHOW']:
        problem_solutions.items.append(None)
    return render_template('index.html', problem_selection_form=problem_selection_form,
            login_form=login_form,
            problem_solutions=problem_solutions.items,
            next_url=next_url, prev_url=prev_url,
            authenticated=current_user.is_authenticated)


@app_bp.route('/problem<problem_id>')
def problem_renderer(problem_id):
    solution = Problem.query.filter_by(problem_id=problem_id).first_or_404()
    return render_template('solution.html', problem_id=problem_id, solution=solution.contents)


@app_bp.errorhandler(404)
def page_not_found_error(error):
    return render_template('404error.html'), 404


@app_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app_bp.index'))


@app_bp.route('/create_solution', methods=['GET', 'POST'])
@login_required
def create_solution():
    # dynamically load allowed file extensions
    file_upload_form = FileUploadForm()
    for extension in db.session.query(Language.extension).all():
        file_upload_form.allowed_extensions.append(extension[0])

    if file_upload_form.validate_on_submit():

        problem_id = file_upload_form.data.get('problem_selection')

        # check problem_id doesn't already exist
        if Problem.query.filter_by(problem_id=problem_id).first() is not None:
            flash('A solution for that problem already exists - please specify an unsolved problem or update the solution')

        else:
            contents = file_upload_form.file_upload.data.read()

            # check content is not null
            if not contents:
                flash("File must not be empty")

            else:
                extension = file_upload_form.file_upload.data.filename.split('.')[-1]
                language = Language.query.filter_by(extension=extension).first()
                language_id = language.language_id
                problem = Problem(problem_id=problem_id, contents=contents, language_id=language_id)
                db.session.add(problem)
                db.session.commit()

    return render_template('create_solution.html', file_upload_form=file_upload_form)


@app_bp.route('/update_solution', methods=['GET', 'POST'])
@login_required
def update_solution():
    # dynamically load allowed file extensions
    file_update_form = FileUpdateForm()
    for extension in db.session.query(Language.extension).all():
        file_update_form.allowed_extensions.append(extension[0])

    if file_update_form.validate_on_submit():
        problem_id = file_update_form.data.get('problem_selection')
        problem_to_update = Problem.query.filter_by(problem_id=problem_id).first()
        if problem_to_update is None:
            flash("Solution does not exist - please try again")
        else:
            contents = file_update_form.file_update.data.read()

            # check content is not null
            if not contents:
                flash("File must not be empty")

            else:
                extension = file_update_form.file_upload.data.filename.split('.')[-1]
                language = Language.query.filter_by(extension=extension).first()
                language_id = language.language_id
                problem_to_update.contents = contents
                problem_to_update.language_id = language_id
                db.session.commit()

    return render_template('update_solution.html', file_update_form=file_update_form)


@app_bp.route('/delete_solution', methods=['GET', 'POST'])
@login_required
def delete_solution():
    file_delete_form = FileDeleteForm()
    if file_delete_form.validate_on_submit():
        problem_id = file_delete_form.data.get('problem_selection')
        problem_to_delete = Problem.query.filter_by(problem_id=problem_id).first()
        if problem_to_delete is None:
            flash("Solution does not exist - please try again")
        else:
            db.session.delete(problem_to_delete)
            db.session.commit()
    return render_template('delete_solution.html', file_delete_form=file_delete_form)
