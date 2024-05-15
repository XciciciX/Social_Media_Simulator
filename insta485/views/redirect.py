"""
Insta485 explore view.

URLs include:
all redirections
"""
import os
import pathlib
import uuid
import hashlib
import flask
import insta485


@insta485.app.route('/following/', methods=['POST'])
def redirect_following():
    """Redirect /following/ route."""
    # Check if a user has checked in
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    connection = insta485.model.get_db()
    cursor = connection.cursor()

    logname = flask.session['username']
    action_target = flask.request.form['username']
    select_query = (
        "SELECT username2 FROM "
        "following WHERE username1 = ?")
    cursor.execute(select_query, (logname, ))
    logname_followings = cursor.fetchall()

    if flask.request.form['operation'] == 'unfollow':
        for following in logname_followings:
            if action_target == following['username2']:
                cursor1 = connection.cursor()
                delete_query = (
                    "DELETE FROM following "
                    "WHERE username1 = ? AND username2 = ?")
                cursor1.execute(delete_query, (logname, action_target))
                connection.commit()
                if flask.request.args.get('target') is None:
                    return flask.redirect(flask.url_for('show_index'))
                return flask.redirect(flask.request.args.get('target'))
        flask.abort(409)

    # else: flask.request.form['operation'] == 'follow':
    else:
        for following in logname_followings:
            if action_target == following['username2']:
                flask.abort(409)
        cursor2 = connection.cursor()
        cursor2.execute("INSERT INTO following (username1, username2) "
                        "VALUES (?, ?)", (logname, action_target))
        connection.commit()
        if flask.request.args.get('target') is None:
            return flask.redirect(flask.url_for('show_index'))
        return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/likes/', methods=['POST'])
def redirect_likes():
    """Redirect /likes/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        logname = flask.session['username']

    postid = flask.request.form['postid']
    like_status = connection.execute(
        "SELECT * FROM likes "
        "WHERE owner = ? AND postid = ?",
        (logname, postid)
    )
    like_status = like_status.fetchone()
    if flask.request.form['operation'] == 'like':
        if like_status is not None:
            flask.abort(409)
        else:
            connection.execute(
                "INSERT INTO likes (owner, postid) "
                "VALUES (?, ?)",
                (logname, postid)
            )
            connection.commit()
    else:
        if like_status is None:
            flask.abort(409)
        else:
            connection.execute(
                "DELETE FROM likes "
                "WHERE owner = ? AND postid = ?",
                (logname, postid)
            )
            connection.commit()
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/comments/', methods=['POST'])
def redirect_comments():
    """Redirect /comments/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        logname = flask.session['username']

    if flask.request.form['operation'] == 'create':
        text = flask.request.form['text']
        postid = flask.request.form['postid']
        if text == '':
            flask.abort(400)
        connection.execute(
            "INSERT INTO comments (owner, postid, text) "
            "VALUES (?, ?, ?)",
            (logname, postid, text)
        )
        connection.commit()
    else:
        commentid = flask.request.form['commentid']
        comment = connection.execute(
            "SELECT * FROM comments "
            "WHERE commentid = ?",
            (commentid, )
        )
        comment = comment.fetchone()
        if comment['owner'] != logname:
            flask.abort(403)
        else:
            connection.execute(
                "DELETE FROM comments "
                "WHERE commentid = ?",
                (commentid, )
            )
            connection.commit()
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/posts/', methods=['POST'])
def redirect_posts():
    """Redirect /posts/ route."""
    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        logname = flask.session['username']

    if flask.request.form['operation'] == 'create':
        fileobj = flask.request.files['file']
        if fileobj is None:
            flask.abort(400)
        else:
            filename = fileobj.filename
            stem = uuid.uuid4().hex
            suffix = pathlib.Path(filename).suffix.lower()
            uuid_basename = f"{stem}{suffix}"
            path = insta485.app.config["UPLOAD_FOLDER"]
            path = path/uuid_basename
            fileobj.save(path)
            connection.execute(
                "INSERT INTO posts (filename, owner) "
                "VALUES (?, ?)",
                (uuid_basename, logname)
            )
            connection.commit()
    else:
        postid = flask.request.form['postid']
        post = connection.execute(
            "SELECT * FROM posts "
            "WHERE postid = ?",
            (postid, )
        )
        post = post.fetchone()
        if post['owner'] != logname:
            flask.abort(403)
        else:
            connection.execute(
                "DELETE FROM posts "
                "WHERE postid = ?",
                (postid, )
            )
            connection.commit()
            os.remove(insta485.app.config["UPLOAD_FOLDER"]/post['filename'])
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_user',
                                            user_url_slug=logname))
    return flask.redirect(flask.request.args.get('target'))


def accounts_login():
    """Redirect /accounts/login/ route."""
    connection = insta485.model.get_db()
    username = flask.request.form['username']
    inputpassword = flask.request.form['password']
    psw = connection.execute(
        "SELECT password FROM users "
        "WHERE username = ?",
        (username, )
    ).fetchone()
    if psw is None:
        flask.abort(403)
    if (username == '' or inputpassword == ''):
        flask.abort(400)
    psw = psw.get("password")
    algorithm = 'sha512'
    algorithm, salt, stored_hashed_password = psw.split('$')
    # Create a hashlib object for the specified algorithm
    hash_obj = hashlib.new(algorithm)
    # Combine the input password and stored salt
    input_password_salted = salt + inputpassword
    # Update the hash object with the salted input password
    hash_obj.update(input_password_salted.encode('utf-8'))
    # Get the hexadecimal representation of the hashed input password
    input_hashed_password = hash_obj.hexdigest()
    if stored_hashed_password != input_hashed_password:
        flask.abort(403)
    flask.session['username'] = username
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


def accounts_edit(logname):
    """Redirect /accounts/edit/ route."""
    connection = insta485.model.get_db()
    if (flask.request.form['fullname'] == ''
            or flask.request.form['email'] == ''):
        flask.abort(400)
    fullname = flask.request.form['fullname']
    email = flask.request.form['email']
    fileobj = flask.request.files['file']
    if not (fileobj and fileobj.filename):
        user_file = connection.execute(
            "SELECT filename FROM users "
            "WHERE username = ?",
            (logname, )
        ).fetchone()
        connection.execute(
            "UPDATE users SET "
            "fullname = ?, email = ?, filename = ? "
            "WHERE username = ?",
            (fullname, email, user_file['filename'], logname)
        )
        connection.commit()
    else:
        filename = fileobj.filename
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"
        path = insta485.app.config["UPLOAD_FOLDER"]
        path = path/uuid_basename
        fileobj.save(path)
        current_file = connection.execute(
            "SELECT filename FROM users "
            "WHERE username = ?",
            (logname, )
        ).fetchone()
        upload_folder = insta485.app.config["UPLOAD_FOLDER"]
        file_path = pathlib.Path(upload_folder / current_file['filename'])
        os.remove(file_path)
        connection.execute(
            "UPDATE users SET fullname = ?, email = ?, filename = ? "
            "WHERE username = ?",
            (fullname, email, uuid_basename, logname)
        )
        connection.commit()
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


def accounts_delete(logname):
    """Redirect /accounts/delete/ route."""
    connection = insta485.model.get_db()

    # Query databse
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        logname = flask.session['username']

    # remove user icon
    cursor1 = connection.cursor()
    select_query = "SELECT filename FROM users WHERE username = ?"
    cursor1.execute(select_query, (logname, ))
    user_icon = cursor1.fetchone()
    if user_icon:
        user_icon_filename = user_icon['filename']
        uplaod_folder = insta485.app.config['UPLOAD_FOLDER']
        user_icon_filepath = os.path.join(uplaod_folder, user_icon_filename)
        if os.path.exists(user_icon_filepath):
            os.remove(user_icon_filepath)

    # remove all user post
    cursor2 = connection.cursor()
    cursor2.execute("SELECT filename FROM posts WHERE owner = ?", (logname, ))
    post_filenames = cursor2.fetchall()

    for post_filename in post_filenames:
        uplaod_folder = insta485.app.config['UPLOAD_FOLDER']
        post_filepath = os.path.join(uplaod_folder, post_filename['filename'])
        if os.path.exists(post_filepath):
            os.remove(post_filepath)

    cursor1.execute("DELETE FROM users WHERE username = ?", (logname,))
    connection.commit()
    target = flask.request.args.get('target')
    flask.session.clear()
    if target is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target)


def accounts_create():
    """Redirect /accounts/create/ route."""
    connection = insta485.model.get_db()

    variables = {}
    variables["file"] = flask.request.files['file']
    variables["fullname"] = flask.request.form['fullname']
    variables["username"] = flask.request.form['username']
    variables["email"] = flask.request.form['email']
    variables["password"] = flask.request.form['password']

    # Check if any fields are empty
    if (variables["fullname"] == '' or variables["username"] == ''
            or variables["email"] == '' or variables["password"] == ''):
        flask.abort(400)
    if (variables["file"] is None or variables["file"].filename == ''):
        flask.abort(400)

    # check if created username exists in database
    cursor1 = connection.cursor()
    cursor1.execute(
        "SELECT username FROM users WHERE username = ?",
        (variables["username"], ))
    username_exist = cursor1.fetchone()
    if username_exist is not None:
        flask.abort(409)

    # Save file
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(variables["file"].filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    variables['file'].filename = uuid_basename
    file_path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
    variables["file"].save(file_path)

    # Salted password
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + variables["password"]
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    # Save other information
    values = (variables["username"], variables["fullname"], variables["email"],
              variables["file"].filename, password_db_string)
    cursor1.execute(
        "INSERT INTO users (username, fullname, email, filename, password) "
        "VALUES (?, ?, ?, ?, ?)",
        values)
    connection.commit()
    if 'username' not in flask.session:
        flask.session['username'] = variables["username"]

    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


def accounts_password(logname):
    """Redirect /accounts/password/ route."""
    connection = insta485.model.get_db()

    password_dict = {}
    password_dict["password"] = flask.request.form['password']
    password_dict["new_password1"] = flask.request.form['new_password1']
    password_dict["new_password2"] = flask.request.form['new_password2']
    if (password_dict["password"] == ''
            or password_dict["new_password1"] == ''
            or password_dict["new_password2"] == ''):
        flask.abort(400)

    original_psw = connection.execute(
        "SELECT password FROM users "
        "WHERE username = ?",
        (logname, )
    ).fetchone().get("password")

    # print(original_psw)

    algorithm = 'sha512'
    algorithm, salt, stored_hashed_password = original_psw.split('$')

    # Create a hashlib object for the specified algorithm
    hash_obj = hashlib.new(algorithm)

    # Combine the input password and stored salt
    input_password_salted = salt + password_dict["password"]

    # Update the hash object with the salted input password
    hash_obj.update(input_password_salted.encode('utf-8'))

    # Get the hexadecimal representation of the hashed input password
    input_hashed_password = hash_obj.hexdigest()

    if input_hashed_password != stored_hashed_password:
        flask.abort(400)

    hash_obj = hashlib.new(algorithm)
    input_new_password1_salted = salt + password_dict["new_password1"]

    # Update the hash object with the salted input password
    hash_obj.update(input_new_password1_salted.encode('utf-8'))

    # Get the hexadecimal representation of the hashed input password
    input_hashed_new_password1 = hash_obj.hexdigest()
    # print(input_hashed_new_password1)

    if input_hashed_new_password1 == stored_hashed_password:
        flask.abort(403)
    if password_dict["new_password1"] != password_dict["new_password2"]:
        flask.abort(401)

    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password_dict["new_password1"]
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])

    connection.execute(
        "UPDATE users SET password = ?"
        "WHERE username = ?",
        (password_db_string, logname)
    )
    connection.commit()
    if flask.request.args.get('target') is None:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(flask.request.args.get('target'))


@insta485.app.route('/accounts/', methods=['POST'])
def redirect_accounts():
    """Redirect /accounts/ route."""
    # Log in
    if flask.request.form['operation'] == 'login':
        return accounts_login()

    # create account
    if flask.request.form['operation'] == 'create':
        return accounts_create()

    # Query database
    if 'username' not in flask.session:
        flask.abort(403)
    else:
        logname = flask.session['username']

    # edit account
    if flask.request.form['operation'] == 'edit_account':
        return accounts_edit(logname)
    # Delete account
    if flask.request.form['operation'] == 'delete':
        return accounts_delete(logname)
    # update password
    # flask.request.form['operation'] == 'update_password':

    return accounts_password(logname)
