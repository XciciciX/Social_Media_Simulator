"""
Insta485 create view.

URLs include:
/accounts/create
"""
import flask
import insta485


@insta485.app.route('/accounts/create/', methods=["GET"])
def create():
    """Display /account_create/ route."""
    # Query database
    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_edit'))

    return flask.render_template("create.html")
