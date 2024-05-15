"""REST API for likes."""
import flask
import insta485
from insta485.api.resources import authenticate


@insta485.app.route('/api/v1/likes/', methods=['POST'])
def create_likes():
    """Create a new like resource."""
    # Check login and authentication
    if 'username' in flask.session:
        logname3 = flask.session['username']
    else:
        status = authenticate()
        if not status:
            response3 = {
                "message": "Forbidden",
                "status_code": 403
            }
            return flask.jsonify(**response3), 403
        logname3 = flask.session['username']

    # Process postid
    postid = flask.request.args.get('postid')
    connection3 = insta485.model.get_db()
    max_postid = connection3.execute(
        'SELECT MAX(postid) AS max_postid FROM posts'
        ).fetchone()
    max_postid = max_postid["max_postid"]

    # Post IDs that are out of range should return a 404 error.
    if (postid is None) or (int(postid) > max_postid):
        response = {
            "message": "Bad Request",
            "status_code": 404
        }
        return flask.jsonify(**response), 404

    # Check if the like aleady exist
    logname_likes_postid = connection3.execute(
        'SELECT likeid FROM likes WHERE '
        'owner = ? AND postid = ?',
        (logname3, postid)
    ).fetchone()

    # If the “like” already exists, return the like object with a 200 response.
    if logname_likes_postid is not None:
        likeid = logname_likes_postid["likeid"]
        response = {
            "likeid": likeid,
            "url": f"/api/v1/likes/{likeid}/"
        }
        return flask.jsonify(**response), 200

    # Insert new like into database
    connection3.execute(
        'INSERT INTO likes (owner, postid) VALUES (?, ?)',
        (logname3, postid))
    connection3.commit()

    # Get likeid
    likeid = connection3.execute(
        'SELECT MAX(likeid) AS new_likeid FROM likes'
        ).fetchone()['new_likeid']
    print(likeid)

    # Response data
    response = {
        "likeid": f"{likeid}",
        "url": f"/api/v1/likes/{likeid}/"
    }
    print(response)
    return flask.jsonify(**response), 201


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_likes(likeid):
    """Delete a like resource."""
    # Check login and authentication
    if 'username' in flask.session:
        logname4 = flask.session['username']
    else:
        status = authenticate()
        if not status:
            response = {
                "message": "Forbidden",
                "status_code": 403
            }
            return flask.jsonify(**response), 403
        logname4 = flask.session['username']

    # Check if the likeid exist
    connection = insta485.model.get_db()
    like = connection.execute(
        'SELECT * FROM likes WHERE likeid = ?',
        (likeid, )
    ).fetchone()

    # If this likeid does not exist
    if like is None:
        return '', 404

    # Check if the logname user owns the like
    like_owner = like['owner']
    if like_owner != logname4:
        return '', 403

    # else delet this likeid
    connection.execute(
        'DELETE FROM likes WHERE likeid = ?',
        (likeid, )
    )
    connection.commit()
    return '', 204
