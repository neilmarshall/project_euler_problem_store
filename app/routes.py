from flask import redirect, render_template, request, url_for
from app import app
from app.forms import ProblemSelectionForm
from app.models import Filepaths

def parse_solution(filepath):
    with open(filepath) as file:
        return ''.join(file.readlines())


@app.route('/', methods=['GET', 'POST'])
def index():

    # check if routing has come via problem selection form
    form = ProblemSelectionForm()
    if form.validate_on_submit():
        new_page = r'/problem' + str(int(form.problem_selection.data))
        return redirect(new_page)

    # else have navigated directly to home page, or have been redirected
    page = request.args.get('page', 1, type=int)
    problem_solutions = Filepaths.query.order_by('id').paginate(page=page, per_page=app.config['SOLUTIONS_TO_SHOW'])
    next_url = url_for('index', page=problem_solutions.next_num) if problem_solutions.has_next else None
    prev_url = url_for('index', page=problem_solutions.prev_num) if problem_solutions.has_prev else None
    while len(problem_solutions.items) < app.config['SOLUTIONS_TO_SHOW']:
        problem_solutions.items.append(None)
    return render_template('index.html', form=form,
            problem_solutions=problem_solutions.items,
            next_url=next_url, prev_url=prev_url)


@app.route('/problem<problem_id>')
def problem_renderer(problem_id):
    path = Filepaths.query.filter_by(id=problem_id).first_or_404()
    solution = parse_solution(path.filepath)
    return render_template('solution.html', problem_number=problem_id, solution=solution)


@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404error.html'), 404
