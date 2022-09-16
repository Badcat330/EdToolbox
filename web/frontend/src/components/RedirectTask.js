import {Navigate, useLocation, useParams} from 'react-router-dom'
import {getTask} from '../actions/tutoring_system'
import {useEffect, useState} from "react";

let cache = new Map()

export const RedirectTask = () => {
  const { taskId } = useParams()
  let location = useLocation();
  let cacheKey = location.key + taskId;
  let cached = cache.get(cacheKey);

  let [data, setData] = useState(() => {
    // initialize from the cache
    return cached || null;
  });

  let [state, setState] = useState(() => {
    // avoid the fetch if cached
    return cached ? "done" : "loading";
  });

  useEffect(() => {
    if (state === "loading") {
      let controller = new AbortController();
      getTask(taskId, controller.signal).then(response => {
        if (controller.aborted) return;

        let parsedData = JSON.parse(response);

        if (parsedData.redirect === null || parsedData.redirect === undefined) {
          console.warn("Got null redirecting value from server.");
          cache.set(cacheKey, <Navigate to={'/'}/>);
          setData(<Navigate to={'/'}/>);
        } else {
          console.log("Successfully fetched url. Redirecting...");
          window.location.href = parsedData.redirect;
        }
      });
      return () => controller.abort();
    }
  }, [state, cacheKey, taskId]);

  useEffect(() => {
    setState("loading");
  }, [taskId]);

  return data;
}
