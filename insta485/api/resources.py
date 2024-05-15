"""REST API for resources."""
import hashlib
import flask
import insta485


def authenticate():
    """Authenticate user."""
    if not flask.request.authorization:
        return False
    username = flask.request.authorization['username']
    password = flask.request.authorization['password']
    if not username or not password:
        return False
    connection = insta485.model.get_db()
    user_info = connection.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    if user_info is None:
        return False
    user_password = user_info['password']
    algorithm, salt, hash_value = user_password.split('$')
    hash_obj = hashlib.new(algorithm)
    input_password = salt + password
    hash_obj.update(input_password.encode('utf-8'))
    input_password = hash_obj.hexdigest()
    if input_password != hash_value:
        return False
    flask.session['username'] = username
    return True


@insta485.app.route('/api/v1/', methods=['GET'])
def get_api_v1():
    """Return API version 1."""
    context = {
        "comments": "/api/v1/comments/",
        "likes": "/api/v1/likes/",
        "posts": "/api/v1/posts/",
        "url": "/api/v1/"
    }
    return flask.jsonify(**context), 200
