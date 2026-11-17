import {Navigate} from "react-router-dom"
import {Spinner} from "react-bootstrap"

import {useAuth} from "../context"

/**
 * Show the page only to logged-in users. This is a UI convenience:
 * the real protection is on the backend (401/403).
 */
export function RequireAuth({children}) {
    const {loggedIn, checking} = useAuth()

    if (checking) {
        return <Spinner animation="border"/>
    }
    return loggedIn ? children : <Navigate to="/login" replace/>
}
