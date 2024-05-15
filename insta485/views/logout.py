"""
Insta485 index (main) view.

URLs include:
/accounts/logout/
"""
import flask
import insta485


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Display /accounts/logout/ route."""
    flask.session.clear()
    return flask.redirect(flask.url_for('show_login'))
