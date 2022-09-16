export const GET_DATA_SUCCESS = 'GET_DATA_SUCCESS';
export const GET_DATA_TRIGGERED = 'GET_DATA_TRIGGERED';
export const GET_DATA_FAILURE = 'GET_DATA_FAILURE';

export async function getTask(task_id, csignal) {
    const encodedValue = encodeURIComponent(task_id);
    console.log("fetching redirect url from server");
    const response = await fetch(
        `https://management-system-api.azurewebsites.net/tasks?id=${encodedValue}`
        , {signal: csignal})

    return await response.json();
}