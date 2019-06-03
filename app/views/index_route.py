from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from app import db
from app.forms import FileDeleteForm, FileUpdateForm, FileUploadForm, LanguageFilterForm, LoginForm, ProblemSelectionForm
from app.models import Language, Problem, User

app_bp = Blueprint('app_bp', __name__)

@app_bp.route('/', methods=['GET', 'POST'])
@app_bp.route('/index', methods=['GET', 'POST'])
def index():

    # helper function to construct language filter form
    def build_language_filter_form():
        choices = [("", "No filter")]
        for language in db.session.query(Language.language).distinct():
            choices.append((language[0], language[0]))
        language_filter_form = LanguageFilterForm()
        language_filter_form.language_filter.choices = choices
        language_filter_form.language_filter.default = language_filter
        language_filter_form.process()
        return language_filter_form

    # check if routing has come via problem selection form
    problem_selection_form = ProblemSelectionForm()
    if problem_selection_form.validate_on_submit():
        problem_id = str(int(problem_selection_form.problem_selection.data))
        return redirect(url_for('app_bp.problem_renderer', problem_id=problem_id))

    # check if routing has come via login form
    login_form = LoginForm()  # note: test user has credentials ('test', 'pass')
    if login_form.validate_on_submit():
        username, password = login_form.data.get('username'), login_form.data.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Username not recognised or invalid password provided - please try again", "danger")
            return redirect(url_for('app_bp.index'))
        else:
            login_user(user, remember=True)

    # else have navigated directly to home page, or have been redirected
    page = request.args.get('page', 1, type=int)
    language_filter = request.args.get('language_filter', "", type=str)
    if language_filter:
        language_ids = [l.language_id for l in Language.query.filter_by(language=language_filter).all()]
        problem_solutions = Problem.query \
                                   .filter(Problem.language_id.in_(language_ids)) \
                                   .order_by('problem_id') \
                                   .paginate(page=page, per_page=current_app.config['SOLUTIONS_TO_SHOW'])
    else:
        problem_solutions = Problem.query \
                                   .order_by('problem_id') \
                                   .paginate(page=page, per_page=current_app.config['SOLUTIONS_TO_SHOW'])

    next_url = url_for('app_bp.index', page=problem_solutions.next_num,
            language_filter=language_filter) if problem_solutions.has_next else None
    prev_url = url_for('app_bp.index', page=problem_solutions.prev_num,
            language_filter=language_filter) if problem_solutions.has_prev else None

    while len(problem_solutions.items) < current_app.config['SOLUTIONS_TO_SHOW']:
        problem_solutions.items.append(None)

    return render_template('index.html', problem_selection_form=problem_selection_form,
            language_filter_form=build_language_filter_form(),
            login_form=login_form,
            problem_solutions=problem_solutions.items,
            next_url=next_url, prev_url=prev_url,
            authenticated=current_user.is_authenticated)


@app_bp.route('/problem<problem_id>')
def problem_renderer(problem_id):
    from_search = request.args.get('from_search') is not None and request.args['from_search'] == "true"
    solution = Problem.query.filter_by(problem_id=problem_id).first()
    if solution is None:
        flash("Solution does not exist - please try again", "warning")
        return redirect(url_for('app_bp.index'))
    return render_template('solution.html', problem_id=problem_id,
            solution=solution.contents, from_search=from_search)


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
            flash("A solution for that problem already exists - please specify an unsolved problem or update the solution", "warning")

        else:
            title = file_upload_form.data.get('problem_title')
            contents = file_upload_form.file_upload.data.read()
            contents = contents.decode('utf-8').replace('\r\n', '\n')

            # check content is not null
            if not contents:
                flash("File must not be empty", "warning")

            else:
                extension = file_upload_form.file_upload.data.filename.split('.')[-1]
                language = Language.query.filter_by(extension=extension).first()
                language_id = language.language_id
                problem = Problem(problem_id=problem_id, contents=contents,
                        language_id=language_id, title=title)
                db.session.add(problem)
                db.session.commit()
                flash("Solution created", "success")

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


@app_bp.route('/delete_solution', methods=['GET', 'POST'])
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
