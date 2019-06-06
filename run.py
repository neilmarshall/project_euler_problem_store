"""
Entry point for 'flask run' command
"""
from app import create_app, db
from app.models import Language, Problem, User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Launch a Python interpreter pre-populated with an application context"""
    return {'db': db, 'Problem': Problem, 'Language': Language, 'User': User}
