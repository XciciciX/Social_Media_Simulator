"""
Insta485 user view.

URLs include:
/users/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/following/', methods=['GET'])
def show_following(user_url_slug):
    """Display /users/<user_url_slug>/following route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['username']

    # Get current user
    userfullname = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    )
    userfullname = userfullname.fetchone()

    # Does not exist in db
    if userfullname is None:
        flask.abort(404)

    # Get all users
    users = connection.execute(
        "SELECT username, filename "
        "FROM users "
    )
    users = users.fetchall()

    # Get following status
    following_dict = {}
    for tmpuser in users:
        is_following = False

        if logname != tmpuser:
            following_count = connection.execute(
                "SELECT username1 "
                "FROM following "
                "WHERE username1 = ? AND username2 = ?",
                (logname, tmpuser['username'])
            ).fetchall()

            if len(following_count) > 0:
                is_following = True

        following_dict[tmpuser['username']] = is_following
        print(following_dict)

    # Get following
    followings = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (user_url_slug, )
    )
    followings = followings.fetchall()

    context = {
        'username': user_url_slug,
        'logname': logname,
        'users': users,
        'userfullname': userfullname,
        'followings': followings
    }
    return flask.render_template("following.html", dictionary1=context,
                                 dictionary2=following_dict)
