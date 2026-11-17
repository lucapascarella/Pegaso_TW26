import {useEffect, useState} from "react"

/**
 * Like useState, but the value is also saved in the browser localStorage.
 */
export function useLocalStorage(key, defaultValue) {
    const [value, setValue] = useState(() => {
        try {
            const saved = window.localStorage.getItem(key)
            return saved !== null ? JSON.parse(saved) : defaultValue
        } catch {
            return defaultValue
        }
    })

    useEffect(() => {
        try {
            if (value === null || value === undefined) {
                window.localStorage.removeItem(key)
            } else {
                window.localStorage.setItem(key, JSON.stringify(value))
            }
        } catch {
            // storage not available (private mode, quota): keep the value in memory only
        }
    }, [key, value])

    return [value, setValue]
}
