"""
Insta485 post view.

URLs include:
/posts/
"""
import flask
import insta485


@insta485.app.route('/accounts/password/', methods=['GET'])
def show_password():
    """Display /accounts/password/ route."""
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']

    select_query = "SELECT * FROM users"
    user = connection.execute(select_query).fetchall()
    context = {'user': user, 'logname': logname}

    return flask.render_template('password.html', **context)
