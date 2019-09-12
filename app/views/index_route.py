"""Routes controlling landing page and login / logout functionality"""

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from app import db
from app.forms import LanguageFilterForm, LoginForm, ProblemSelectionForm
from app.models import Language, Problem, User

import sqlalchemy.exc

app_bp = Blueprint('app_bp', __name__)

@app_bp.errorhandler(sqlalchemy.exc.OperationalError)
def handler_error(e):
    current_app.logger.error(e)
    return render_template('500error.html')


@app_bp.route('/', methods=['GET', 'POST'])
@app_bp.route('/index', methods=['GET', 'POST'])
def index():
    """Route controlling landing page"""

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
        if user and user.check_password(password):
            login_user(user, remember=True)
        else:
            flash("Username not recognised or invalid password provided - please try again", "danger")
            return redirect(url_for('app_bp.index'))

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
    """Route controlling rendering of problem solutions"""
    from_search = request.args.get('from_search') is not None and request.args['from_search'] == "true"
    solution = Problem.query.filter_by(problem_id=problem_id).first()
    if solution is None:
        flash("Solution does not exist - please try again", "warning")
        return redirect(url_for('app_bp.index'))
    return render_template('solution.html', problem_id=problem_id,
                           solution=solution.contents, from_search=from_search)


@app_bp.route('/logout')
def logout():
    """Route controlling logging out of users"""
    logout_user()
    return redirect(url_for('app_bp.index'))
