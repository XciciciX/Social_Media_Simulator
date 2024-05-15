"""
Insta485 explore view.

URLs include:
/explore/
"""
import flask
import insta485


@insta485.app.route('/explore/', methods=['GET'])
def show_explore():
    """Display /explore/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']

    # Get not following
    not_following = connection.execute(
        "SELECT username, filename "
        "FROM users "
        "WHERE username NOT IN (SELECT username2 "
        "FROM following WHERE username1 = ?) "
        "AND username != ?",
        (logname, logname)
    ).fetchall()
    context = {'not_following': not_following, 'logname': logname}
    return flask.render_template("explore.html", **context)
