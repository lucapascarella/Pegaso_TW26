import {useEffect, useRef, useState} from "react"

import {fetchWrapper} from "../_services/fetchWrapper.js"

/**
 * Open the Server-Sent Events stream and call onEvent(name, data) for every event.
 *
 * EventSource cannot send the Authorization header, so before every (re)connection
 * the hook asks the API for a short-lived stream token (60 s) and puts it in the URL.
 */
export function useSSE(token, events, onEvent, reconnectSec = 5) {
    const [connected, setConnected] = useState(false)
    const [error, setError] = useState(null)

    // Always call the latest callback without reopening the connection at every render
    const handler = useRef(onEvent)
    handler.current = onEvent

    useEffect(() => {
        if (!token) return

        let source = null
        let timeout = null
        let closed = false

        async function connect() {
            try {
                const resp = await fetchWrapper.post("/api/stream/token", null, token)
                if (closed) return
                source = new EventSource(`/api/stream?token=${encodeURIComponent(resp.stream_token)}`)

                source.onopen = () => {
                    setConnected(true)
                    setError(null)
                }
                events.forEach(name => source.addEventListener(name, e => handler.current(name, JSON.parse(e.data))))

                source.onerror = () => {
                    // Close and reconnect with a NEW token (the old one may be expired)
                    setConnected(false)
                    setError(`Connessione in tempo reale persa: nuovo tentativo tra ${reconnectSec} s`)
                    source.close()
                    timeout = setTimeout(connect, reconnectSec * 1000)
                }
            } catch (err) {
                setError(err.message)
                timeout = setTimeout(connect, reconnectSec * 1000)
            }
        }

        connect()

        // Cleanup when the component unmounts or the token changes
        return () => {
            closed = true
            clearTimeout(timeout)
            source?.close()
            setConnected(false)
        }
    }, [token])

    return {connected, error}
}
