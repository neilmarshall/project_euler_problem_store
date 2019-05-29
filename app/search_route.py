from flask import Blueprint, redirect, request, url_for
from app import db
from app.models import Language, Problem, User
from app.routes import app_bp

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search')
def search_router():
    search_string = request.args.get('search_for', None)
    if search_string:
        search_result = db.session \
                          .query(Problem.problem_id) \
                          .filter(Problem.contents.ilike(f'%{search_string}%')) \
                          .all()
        search_result = map(lambda result: result[0], search_result)
        print(list(search_result))
    return redirect(url_for('app_bp.index'))
