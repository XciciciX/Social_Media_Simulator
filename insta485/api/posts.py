"""REST API for posts."""
import flask
import insta485
from insta485.api.resources import authenticate


@insta485.app.route('/api/v1/posts/', methods=['GET'])
def get_post_index():
    """Return the 10 newest posts."""
    if 'username' in flask.session:
        logname5 = flask.session['username']
    else:
        status = authenticate()
        if not status:
            context = {
                "message": "Forbidden",
                "status_code": 403
            }
            return flask.jsonify(**context), 403
        logname5 = flask.session['username']
    page = flask.request.args.get('page', default=0, type=int)
    size = flask.request.args.get('size', default=10, type=int)
    if size < 0 or page < 0:
        context = {
            "message": "Bad Request",
            "status_code": 400,
            "logname": logname5
        }
        return flask.jsonify(**context), 400
    postid_lte = flask.request.args.get('postid_lte', default=None, type=int)
    connection = insta485.model.get_db()
    # direct to the most recent if postid_lte is not specified
    if postid_lte is None:
        post_latest = connection.execute(
            'SELECT * FROM posts '
            'ORDER BY postid DESC'
        ).fetchone()
        postid_lte = post_latest['postid']
    post_list = connection.execute(
        'SELECT postid FROM posts '
        'WHERE (owner IN ( '
        'SELECT username2 FROM following WHERE username1 = ?) '
        'OR owner = ?) '
        'AND postid <= ? '
        'ORDER BY postid DESC '
        'LIMIT ? OFFSET ?',
        (logname5, logname5, postid_lte, size, page * size)
    ).fetchall()
    next_url = ''
    if len(post_list) == size:  # At most size posts
        next_url = (f"/api/v1/posts/?size={size}&page={page+1}"
                    f"&postid_lte={post_list[0]['postid']}")
    results = []
    for this_post in post_list:
        results.append({
            "postid": this_post['postid'],
            "url": f"/api/v1/posts/{this_post['postid']}/"
        })
    # get url of the command
    if len(flask.request.args) == 0:
        url = flask.request.path
    else:
        url = flask.request.full_path
    context = {
        "next": next_url,
        "results": results,
        "url": url
    }
    return flask.jsonify(**context), 200


@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/', methods=['GET'])
def get_post(postid_url_slug):
    """Return post on postid."""
    if 'username' in flask.session:
        logname = flask.session['username']
    else:
        # status = authenticate()
        if not authenticate():
            context = {
                "message": "Forbidden",
                "status_code": 403
            }
            return flask.jsonify(**context), 403
        logname = flask.session['username']
    connection = insta485.model.get_db()
    # Post IDs that are out of range
    post_postid = connection.execute(
        'SELECT * FROM posts '
        'WHERE postid = ? ',
        (postid_url_slug, )
    ).fetchone()
    if post_postid is None:
        context = {
            "message": "Not Found",
            "status_code": 404
            }
        return flask.jsonify(**context), 404
    comment_list = connection.execute(
        'SELECT * FROM comments '
        'WHERE postid = ? '
        'ORDER BY commentid ASC ',
        (postid_url_slug, )
    ).fetchall()
    comments_all = []
    for this_comment in comment_list:
        ownthis = this_comment['owner'] == logname
        comments_all.append({
            "commentid": this_comment['commentid'],
            "lognameOwnsThis": ownthis,
            "owner": this_comment['owner'],
            "ownerShowUrl": f"/users/{this_comment['owner']}/",
            "text": this_comment['text'],
            "url": f"/api/v1/comments/{this_comment['commentid']}/"
        })
    like_list = connection.execute(
        'SELECT * FROM likes '
        'WHERE postid = ? ',
        (postid_url_slug, )
    ).fetchall()
    # numlikes = len(like_list)
    loglikethis = False
    like_url = None
    for this_like in like_list:
        if this_like['owner'] == logname:
            loglikethis = True
            like_url = f"/api/v1/likes/{this_like['likeid']}/"
            break
    like_info = {
        "lognameLikesThis": loglikethis,
        "numLikes": len(like_list),
        "url": like_url
    }
    owner_info = connection.execute(
        'SELECT filename FROM users '
        'WHERE username = ? ',
        (post_postid['owner'], )
    ).fetchone()
    context = {
        "comments": comments_all,
        "comments_url": f"/api/v1/comments/?postid={postid_url_slug}",
        "created": post_postid['created'],
        "imgUrl": f"/uploads/{post_postid['filename']}",
        "likes": like_info,
        "owner": post_postid['owner'],
        "ownerImgUrl": f"/uploads/{owner_info['filename']}",
        "ownerShowUrl": f"/users/{post_postid['owner']}/",
        "postShowUrl": f"/posts/{postid_url_slug}/",
        "postid": postid_url_slug,
        "url": f"/api/v1/posts/{postid_url_slug}/"
    }
    return flask.jsonify(**context), 200
