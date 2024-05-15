"""
Insta485 index (main) view.

URLs include:
/accounts/auth/
"""
import flask
import insta485


@insta485.app.route('/accounts/auth/', methods=['GET'])
def auth():
    """Display /accounts/auth/ route."""
    # Query database
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        return '', 200
