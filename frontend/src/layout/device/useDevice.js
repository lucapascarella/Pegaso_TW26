import {useEffect, useState} from "react"

import {fetchWrapper} from "../../_services/fetchWrapper.js"
import {useAuth} from "../../context"

const api = "/api/devices"

const endpointList = (offset, limit) => `${api}/list?offset=${offset}&limit=${limit}`
const endpointCount = () => `${api}/count`

/**
 * Paginated device list. Every change of page triggers a new request;
 * the AbortController cancels the previous one if it is still running.
 */
export function useDeviceList(pageSize = 25) {
    const {token, logout} = useAuth()
    const [list, setList] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [pageIndex, setPageIndex] = useState(0)
    const [reload, setReload] = useState(0)

    useEffect(() => {
        const controller = new AbortController()
        setLoading(true)
        setError(null)

        fetchWrapper.get(endpointList(pageIndex * pageSize, pageSize), token, controller.signal)
            .then(resp => setList(resp.data))
            .catch(err => {
                if (err.name === "AbortError") return
                if (err.status === 401) logout()   // token expired
                setError(err.message)
            })
            .finally(() => setLoading(false))

        return () => controller.abort()
    }, [token, pageIndex, pageSize, reload])

    return {list, setList, loading, error, pageIndex, setPageIndex, reload: () => setReload(r => r + 1)}
}

export function useDeviceCount() {
    const {token} = useAuth()
    const [count, setCount] = useState(0)

    useEffect(() => {
        const controller = new AbortController()
        fetchWrapper.get(endpointCount(), token, controller.signal)
            .then(resp => setCount(resp.data))
            .catch(() => setCount(0))
        return () => controller.abort()
    }, [token])

    return count
}
