from app import create_app
from flask import render_template

_app = create_app()
_app.secret_key = 'struggle'


@_app.before_first_request
def create_db():
    from app.models import db
    db.create_all()

@_app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@_app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    _app.run(debug=True)
