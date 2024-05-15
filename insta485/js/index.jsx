import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Index({ url }) {
  /* Display image and post owner of a single post */

  const [posts, setPosts] = useState([]);
  const [isHasMore, setIsHasMore] = useState(true);
  const [nextUrl, setNextUrl] = useState("");

  useEffect(() => {
    window.scrollTo(0, 0);
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
          setPosts(data.results);
          setNextUrl(data.next);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  const NextPage = () => {
    let ignoreStaleRequest = false;
    if (nextUrl !== "") {
      fetch(nextUrl, { credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          if (!ignoreStaleRequest) {
            setPosts((prevPosts) => [...prevPosts, ...data.results]);
            setNextUrl(data.next);
            setIsHasMore(data.next !== null);
          }
        })
        .catch((error) => {
          console.log(error);
          setIsHasMore(false);
        });
    } else {
      setIsHasMore(false);
    }
    return () => {
      ignoreStaleRequest = true;
    };
  };

  return (
    <InfiniteScroll
      dataLength={posts.length}
      next={NextPage}
      hasMore={isHasMore}
      loader={<h4>Loading...</h4>}
      endMessage={
        <p style={{ textAlign: "center" }}>
          <b>These are all insta485 posts!</b>
        </p>
      }
    >
      {posts.map((post) => (
        <Post url={post.url} key={post.postid} />
      ))}
    </InfiniteScroll>
  );
}

Index.propTypes = {
  url: PropTypes.string.isRequired,
};
