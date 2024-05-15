"""
Insta485 user view.

URLs include:
/users/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/', methods=['GET'])
def show_user(user_url_slug):
    """Display /users/<user_url_slug> route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect('/accounts/login/')

    logname = flask.session['username']

    # Get this user's info
    userinfo = connection.execute(
        "SELECT fullname "
        "FROM users "
        "WHERE username = ?",
        (user_url_slug, )
    ).fetchone()
    # Does not exist in db
    if userinfo is None:
        flask.abort(404)
    # Get following status
    is_following = False
    if flask.session['username'] != user_url_slug:
        followingstatus = connection.execute(
            "SELECT username1, username2 "
            "FROM following "
            "WHERE username1 = ? AND username2 = ?",
            (flask.session['username'], user_url_slug)
        ).fetchone()
        if followingstatus is not None:
            is_following = True
    # Get posts
    posts_num = connection.execute(
        "SELECT COUNT(*) as num_posts "
        "FROM posts "
        "WHERE owner = ?",
        (user_url_slug, )
    ).fetchone()
    posts = connection.execute(
        "SELECT postid, filename "
        "FROM posts "
        "WHERE owner = ?",
        (user_url_slug, )
    ).fetchall()
    # Get followers
    followers = connection.execute(
        "SELECT COUNT(*) as num_followers "
        "FROM following "
        "WHERE username2 = ?",
        (user_url_slug, )
    ).fetchone()
    # Get following
    following = connection.execute(
        "SELECT COUNT(*) as num_following "
        "FROM following "
        "WHERE username1 = ?",
        (user_url_slug, )
    ).fetchone()
    context = {
        'username': user_url_slug,
        'logname': logname,
        'users': userinfo,
        'is_following': is_following,
        'posts_num': posts_num,
        'posts': posts,
        'followers': followers,
        'following': following
    }
    return flask.render_template("user.html", **context)
