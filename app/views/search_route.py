from flask import Blueprint, redirect, render_template, request, url_for
from app import db
from app.models import Problem

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search')
def search_router():
    search_for = request.args.get('search_for', None)

    if not search_for:
        return redirect(url_for('app_bp.index'))

    search_results = db.session \
                       .query(Problem) \
                       .filter(Problem.contents.ilike(f'%{search_for}%')) \
                       .all()

    if not search_results:
        return render_template('search_results_null.html',
                               search_for=search_for)

    return render_template('search_results.html',
                           search_results=search_results,
                           search_for=search_for)
