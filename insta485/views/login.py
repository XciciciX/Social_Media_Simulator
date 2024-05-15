"""
Insta485 post view.

URLs include:
/posts/
"""
import flask
import insta485


@insta485.app.route('/accounts/login/', methods=['GET'])
def show_login():
    """Display /accounts/login page."""
    # Connect to database
    connection = insta485.model.get_db()

    if 'username' in flask.session:
        return flask.redirect(flask.url_for('show_index'))

    # Get Users
    users_key = connection.execute(
        "SELECT username, password "
        "FROM users "
    )
    users_key = users_key.fetchall()

    context = {'users_key': users_key}

    return flask.render_template('login.html', **context)
