const defaultMessage = "Request failed with no error message from the server."

/**
 * Send a request to the API and return the parsed JSON body.
 * The backend always answers with {success, message, data}: on errors the message becomes the Error message.
 */
async function request(method, url, {body = null, token = null, signal = null, form = false} = {}) {
    const headers = {}
    let payload = undefined

    if (form) {
        // OAuth2 login: application/x-www-form-urlencoded
        payload = new URLSearchParams(body)
    } else if (body !== null) {
        headers["Content-Type"] = "application/json"
        payload = JSON.stringify(body)
    }
    if (token) {
        headers["Authorization"] = `Bearer ${token}`
    }

    const resp = await fetch(url, {method, headers, body: payload, signal})

    let data = null
    try {
        data = await resp.json()
    } catch {
        // empty or non-JSON body
    }

    if (!resp.ok) {
        const error = new Error(data?.message || defaultMessage)
        error.status = resp.status
        error.data = data?.data
        throw error
    }
    return data
}

export const fetchWrapper = {
    get: (url, token, signal) => request("GET", url, {token, signal}),
    post: (url, body, token) => request("POST", url, {body, token}),
    put: (url, body, token) => request("PUT", url, {body, token}),
    delete: (url, token) => request("DELETE", url, {token}),
    postForm: (url, body) => request("POST", url, {body, form: true}),
}
