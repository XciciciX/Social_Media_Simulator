"""REST API for comments."""
import flask
import insta485
from insta485.api.resources import authenticate


@insta485.app.route('/api/v1/comments/', methods=['POST'])
def create_comments():
    """Create a new comment resource."""
    # Check login and authentication
    if 'username' in flask.session:
        logname1 = flask.session['username']
    else:
        status = authenticate()
        if not status:
            response1 = {
                "message": "Forbidden",
                "status_code": 403
            }
            return flask.jsonify(**response1), 403
        logname1 = flask.session['username']

    # Process postid
    postid1 = flask.request.args.get('postid')
    connection1 = insta485.model.get_db()
    max_postid = connection1.execute(
        'SELECT MAX(postid) AS max_postid FROM posts'
        ).fetchone()
    max_postid = max_postid["max_postid"]

    # Post IDs that are out of range should return a 404 error.
    if (postid1 is None) or (int(postid1) > max_postid):
        response = {
            "message": "Bad Request",
            "status_code": 404
        }
        return flask.jsonify(**response), 404

    # Insert new comments
    text = flask.request.get_json(force=True)['text']
    connection1.execute(
        "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
        (logname1, postid1, text)
    )
    commentid = connection1.execute(
        "SELECT MAX(commentid) AS max_commentid FROM comments"
    ).fetchone()["max_commentid"]
    connection1.commit()

    # Response
    response = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": logname1,
        "ownerShowUrl": f"/users/{logname1}/",
        "text": text,
        "url": f"/api/v1/comments/{commentid}/"
    }
    return flask.jsonify(**response), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comments(commentid):
    """Delete a comment resource."""
    # Check login and authentication
    if 'username' in flask.session:
        logname2 = flask.session['username']
    else:
        status = authenticate()
        if not status:
            response2 = {
                "message": "Forbidden",
                "status_code": 403
            }
            return flask.jsonify(**response2), 403
        logname2 = flask.session['username']

    # Check if commentid exists
    connection2 = insta485.model.get_db()
    comment = connection2.execute(
        "SELECT * FROM comments WHERE commentid = ?",
        (commentid, )).fetchone()
    # If the commentid does not exist, return 404.
    if comment is None:
        return '', 404
    # If the user doesn’t own the comment, return 403.
    comment_owner = comment["owner"]
    if comment_owner != logname2:
        return '', 403

    # Delete this comment
    connection2.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid, )
    )
    connection2.commit()
    return '', 204
