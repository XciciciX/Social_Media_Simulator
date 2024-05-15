import React from "react";
import PropTypes from "prop-types";

export default function CommentBlock({ comments, setComments, commentsUrl }) {
  if (!comments) {
    return <div />;
  }
  return (
    <div>
      {comments.map((comment) => (
        <CommentRow
          key={comment.commentid}
          comment={comment}
          setComments={setComments}
        />
      ))}
      <AddComment commentsUrl={commentsUrl} setComments={setComments} />
    </div>
  );
}

function CommentRow({ comment, setComments }) {
  if (comment.lognameOwnsThis) {
    return (
      <div>
        <a href={comment.ownerShowUrl}>{comment.owner}</a>
        <span data-testid="comment-text">{comment.text}</span>
        <DeleteComment
          commentidUrl={comment.url}
          commentId={comment.commentid}
          setComments={setComments}
        />
      </div>
    );
  }
  return (
    <div>
      <a href={comment.ownerShowUrl}>{comment.owner}</a>
      <span data-testid="comment-text">{comment.text}</span>
    </div>
  );
}

function AddComment({ commentsUrl, setComments }) {
  let outputdiv = <div />;
  const handleEnter = (e) => {
    let ignoreStaleRequest = false;
    e.preventDefault();
    if (e.key === "Enter") {
      e.preventDefault();
      if (commentsUrl !== "") {
        if (e.target.value !== "") {
          console.log(commentsUrl);
          console.log("test");
          fetch(commentsUrl, {
            method: "POST",
            credentials: "same-origin",
            body: JSON.stringify({ text: e.target.value }),
          })
            .then((response) => {
              if (!response.ok) throw new Error("Failed to response");
              return response.json();
            })
            .then((data) => {
              if (!ignoreStaleRequest) {
                setComments((prev) => [...prev, data]);
              }
            })
            .catch((error) => console.log(error));
          e.target.value = "";
        }
      }
    }
    return () => {
      ignoreStaleRequest = true;
    };
  };
  const handleSubmit = (e) => {
    e.preventDefault();
  };
  if (commentsUrl !== "") {
    outputdiv = (
      <form data-testid="comment-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Enter comments..."
          onKeyUp={handleEnter}
        />
      </form>
    );
  }
  return outputdiv;
}

function DeleteComment({ commentidUrl, commentId, setComments }) {
  const handleClick = (e) => {
    e.preventDefault();
    fetch(commentidUrl, {
      method: "DELETE",
      credentials: "same-origin",
    })
      .then((response) => {
        if (!response.ok) throw new Error("Failed to delete comment");
      })
      .then(() => {
        setComments((prevComments) =>
          prevComments.filter((comment) => comment.commentid !== commentId),
        );
      })
      .catch((error) => console.log(error));
  };
  return (
    <div>
      <button
        type="button"
        onClick={handleClick}
        data-testid="delete-comment-button"
      >
        Delete
      </button>
    </div>
  );
}

CommentBlock.propTypes = {
  comments: PropTypes.arrayOf(
    PropTypes.shape({
      commentid: PropTypes.number.isRequired,
      lognameOwnsThis: PropTypes.bool.isRequired,
      owner: PropTypes.string.isRequired,
      ownerShowUrl: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
    }),
  ).isRequired,
  setComments: PropTypes.func.isRequired,
  commentsUrl: PropTypes.string.isRequired,
};

AddComment.propTypes = {
  commentsUrl: PropTypes.string.isRequired,
  setComments: PropTypes.func.isRequired,
};

DeleteComment.propTypes = {
  commentidUrl: PropTypes.string.isRequired,
  commentId: PropTypes.number.isRequired,
  setComments: PropTypes.func.isRequired,
};

CommentRow.propTypes = {
  comment: PropTypes.shape({
    commentid: PropTypes.number.isRequired,
    lognameOwnsThis: PropTypes.bool.isRequired,
    owner: PropTypes.string.isRequired,
    ownerShowUrl: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
  }).isRequired,
  setComments: PropTypes.func.isRequired,
};
