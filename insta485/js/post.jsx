import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import CommentBlock from "./comment";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [created, setCreated] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [likes, setLikes] = useState(null);
  const [liked, setLiked] = useState(null);
  const [likesurl, setLikesurl] = useState("");
  const [postid, setPostid] = useState(0);
  const [likeflag, setLikeflag] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentsUrl, setCommentsUrl] = useState("");

  // let ignoreStaleRequest = false;
  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          const time = dayjs(data.created).utc(true).fromNow();
          setCreated(time);
          setPostShowUrl(data.postShowUrl);
          setOwnerShowUrl(data.ownerShowUrl);
          setOwnerImgUrl(data.ownerImgUrl);
          setLikes(data.likes.numLikes);
          setLiked(data.likes.lognameLikesThis);
          setLikesurl(data.likes.url);
          setPostid(data.postid);
          setComments(data.comments);
          setCommentsUrl(data.comments_url);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url, liked]);

  function handleLikeClick() {
    if (!liked) {
      const likeurl = `/api/v1/likes/?postid=${postid}`;
      fetch(likeurl, {
        method: "POST",
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw Error("Failed to like this post");
          return response.json();
        })
        .then(() => {
          // if (!ignoreStaleRequest) {
          setLikes(likes + 1);
          setLiked(true);
          setLikeflag(!likeflag);
          // }
        })
        .catch((error) => console.log(error));
    } // if
    else {
      fetch(likesurl, {
        method: "DELETE",
        credentials: "same-origin",
      })
        .then((response) => {
          if (!response.ok) throw Error("Failed to unlike this post");
          // return response.json();
        })
        .then(() => {
          // if (!ignoreStaleRequest) {
          setLikes(likes - 1);
          setLiked(false);
          setLikeflag(!likeflag);
          // }
        })
        .catch((error) => console.log(error));
    } // else
  }

  function handleDoubleClick() {
    if (!liked) {
      handleLikeClick();
    }
  }

  if (likes === null || liked === null) {
    return <div>Loading...</div>;
  }
  // Render post image and post owner
  return (
    <div className="post">
      <p>
        <a href={ownerShowUrl}>
          <img src={ownerImgUrl} width="20" height="20" alt="owner_image" />
        </a>
        <a href={ownerShowUrl}>{owner}</a>
        <a href={postShowUrl}>{created}</a>
      </p>
      <img src={imgUrl} alt="post_image" onDoubleClick={handleDoubleClick} />
      <br />
      <button
        onClick={handleLikeClick}
        type="button"
        data-testid="like-unlike-button"
      >
        {liked ? "Unlike" : "Like"}
      </button>
      {likes} {likes !== 1 ? "likes" : "like"}
      <div>
        <div>{CommentBlock({ comments, setComments, commentsUrl })}</div>
      </div>
    </div>
  );
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
