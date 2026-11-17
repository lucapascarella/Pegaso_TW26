import {createContext, useContext, useEffect, useState} from "react"

import {fetchWrapper} from "../_services/fetchWrapper.js"
import {useLocalStorage} from "../hooks"

const AuthContext = createContext(null)

export function useAuth() {
    return useContext(AuthContext)
}

export function AuthProvider({children}) {
    const [token, setToken] = useLocalStorage("token", null)
    const [user, setUser] = useState(null)
    const [checking, setChecking] = useState(!!token)

    // Derived values
    const loggedIn = !!(token && user)
    const role = user?.role
    const canEdit = role === "admin" || role === "operator"

    /**
     * At start (or when the token changes) ask the backend who the token belongs to.
     * An expired or invalid token logs the user out.
     */
    useEffect(() => {
        const controller = new AbortController()
        if (!token) {
            setUser(null)
            setChecking(false)
            return
        }
        setChecking(true)
        fetchWrapper.get("/api/auth/me", token, controller.signal)
            .then(resp => setUser(resp.data))
            .catch(err => {
                if (err.name !== "AbortError") {
                    setToken(null)
                }
            })
            .finally(() => setChecking(false))

        return () => controller.abort()
    }, [token])

    async function login(email, password) {
        const resp = await fetchWrapper.postForm("/api/auth/token", {username: email, password})
        setToken(resp.access_token)
    }

    function logout() {
        setToken(null)
        setUser(null)
    }

    const value = {token, user, role, canEdit, loggedIn, checking, login, logout}
    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
