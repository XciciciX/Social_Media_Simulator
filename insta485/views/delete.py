"""
Insta485 delete view.

URLs include:
/accounts/delete
"""
import flask
import insta485


@insta485.app.route('/accounts/delete/', methods=["GET"])
def delete():
    """Display /account_delete/ route."""
    # Connect to database
    # Connect to database
    # connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']

    context = {'logname': logname}
    return flask.render_template("delete.html", **context)
