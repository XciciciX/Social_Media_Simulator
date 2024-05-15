"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import arrow
import insta485


@insta485.app.route('/', methods=['GET'])
def show_index():
    """Display / route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']

    # Get following and himself
    followings = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (flask.session['username'], )
    ).fetchall()
    followings.append({'username2': flask.session['username']})
    # Get users
    users = connection.execute(
        "SELECT username, filename "
        "FROM users"
    ).fetchall()
    # Get posts
    posts = connection.execute(
        "SELECT postid, owner, filename, created "
        "FROM posts "
        "ORDER BY postid DESC"
    ).fetchall()
    current_time = arrow.utcnow()
    for post in posts:
        post['created'] = arrow.get(post['created']).humanize(current_time)
    # Get likes
    likes = connection.execute(
        "SELECT p.postid, IFNULL(COUNT(l.postid), 0) AS num_likes "
        "FROM posts p "
        "LEFT JOIN likes l ON p.postid = l.postid "
        "GROUP BY p.postid"
    ).fetchall()
    # Queue likes
    user_likes = connection.execute(
        "SELECT postid "
        "FROM likes "
        "WHERE owner = ?",
        (flask.session['username'], )
    ).fetchall()
    # Queue unlikes
    user_unlikes = []
    for post_id in posts:
        if post_id['postid'] not in [user_like['postid'] for
                                     user_like in user_likes]:
            user_unlikes.append({'postid': post_id['postid']})
    # Get comments
    comments = connection.execute(
        "SELECT owner, postid, text "
        "FROM comments"
    ).fetchall()

    # Add database info to context
    context = {"posts": posts, "logname": logname, "users": users,
               "likes": likes, "user_likes": user_likes,
               "user_unlikes": user_unlikes, "comments": comments,
               "followings": followings}
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>', methods=['GET'])
def show_image(filename):
    """Show the uploaded image."""
    if 'username' not in flask.session:
        flask.abort(403)
    connection = insta485.model.get_db()
    postfiles = connection.execute(
        "SELECT filename FROM posts "
        "WHERE filename = ?",
        (filename, )
    ).fetchall()
    userfiles = connection.execute(
        "SELECT filename FROM users "
        "WHERE filename = ?",
        (filename, )
    ).fetchall()
    if (len(postfiles) == 0 and len(userfiles) == 0):
        flask.abort(404)
    return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                     filename)
