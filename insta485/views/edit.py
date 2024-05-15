"""
Insta485 explore view.

URLs include:
/accounts/edit/
"""
import flask
import insta485


@insta485.app.route('/accounts/edit/', methods=['GET'])
def show_edit():
    """Display /accounts/edit/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']

    # Get user detail
    query = "SELECT * FROM users WHERE username = ?"
    user = connection.execute(query, (logname, )).fetchone()
    context = {'user': user, 'logname': logname}
    return flask.render_template("edit.html", **context)
