"""
Insta485 followers view.

URLs include:
/users/<user_url_slug>/followers/
"""
import flask
import insta485


@insta485.app.route('/users/<user_url_slug>/followers/', methods=["GET"])
def followers(user_url_slug):
    """Display /users/<user_url_slug>/followers/ route."""
    # Connect to database
    connection = insta485.model.get_db()
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Query database
    # Check if user_url_slug exists in the database
    cursor_dict = {}
    cursor_dict["cursor1"] = connection.cursor()
    cursor_dict["cursor1"].execute(
        "SELECT username FROM users WHERE username = ?", (user_url_slug, ))
    user_url_data = cursor_dict["cursor1"].fetchone()
    if user_url_data is None:
        flask.abort(404)

    # If ser_url_slug exists, access followers
    else:
        # Get loggedin username
        logname = flask.session['username']

        # Find the followers of user_url_slug
        cursor_dict["cursor2"] = connection.cursor()
        cursor_dict["cursor2"].execute(
            "SELECT username1 FROM following WHERE username2 = ?",
            (user_url_slug, ))
        followers_all = cursor_dict["cursor2"].fetchall()

        # Find loggedin user's following
        cursor_dict["cursor3"] = connection.cursor()
        cursor_dict["cursor3"].execute(
            "SELECT username2 FROM following WHERE username1 = ?", (logname, ))
        logname_followings = cursor_dict["cursor3"].fetchall()

        # Check if loggedin user is following the followers of user_url_slug
        logname_is_following = []
        # print(followers)
        # print(logname_followings) list of dictionary!!

        for follower in followers_all:
            cursor_dict["flag"] = False
            for logname_following in logname_followings:
                if follower['username1'] == logname_following['username2']:
                    logname_is_following.append(True)
                    cursor_dict["flag"] = True
            if not cursor_dict["flag"]:
                logname_is_following.append(False)

        followers_with_booleans = []
        for follower, boolean in zip(followers_all, logname_is_following):
            cursor_dict["cursor4"] = connection.cursor()
            cursor_dict["cursor4"].execute(
                "SELECT filename FROM users WHERE username = ?",
                (follower['username1'], ))
            icon_filename = cursor_dict["cursor4"].fetchone()
            combined = {'username': follower['username1'],
                        'logname_is_following': boolean,
                        'filename': icon_filename['filename']}
            followers_with_booleans.append(combined)

        context = {'followers': followers_with_booleans,
                   'logname': logname,
                   'user': user_url_slug}

    return flask.render_template("followers.html", **context)
