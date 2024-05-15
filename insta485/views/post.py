"""
Insta485 post view.

URLs include:
/posts/
"""
import flask
import arrow
import insta485


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def show_post(postid_url_slug):
    """Display /posts/<postid_url_slug>/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']

    # Get post
    post = connection.execute(
        "SELECT postid, owner, filename, created "
        "FROM posts "
        "WHERE postid = ?",
        (postid_url_slug, )
    ).fetchone()
    current_time = arrow.utcnow()
    if post is None:
        flask.abort(404)
    post['created'] = arrow.get(post['created']).humanize(current_time)
    # Get owner
    owner = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (post['owner'], )
    ).fetchone()
    # Get likes
    likes = connection.execute(
        "SELECT COUNT(*) AS num_likes "
        "FROM likes "
        "WHERE postid = ?",
        (postid_url_slug, )
    ).fetchone()
    # Get like status
    like_status = connection.execute(
        "SELECT owner "
        "FROM likes "
        "WHERE postid = ? AND owner = ?",
        (postid_url_slug, flask.session['username'])
    ).fetchone()
    # Get comments
    comments = connection.execute(
        "SELECT commentid, owner, text "
        "FROM comments "
        "WHERE postid = ?",
        (postid_url_slug, )
    ).fetchall()

    contexts = {
        'logname': logname,
        'post': post,
        'owner': owner,
        'likes': likes,
        'like_status': like_status,
        'comments': comments,
    }
    return flask.render_template("post.html", **contexts)
