import {useState} from "react"
import {Alert, Button, Card, Form} from "react-bootstrap"
import {Navigate} from "react-router-dom"

import {useAuth} from "../../context"

export function Login() {
    const {login, loggedIn} = useAuth()

    // Controlled form: React state is the single source of truth for the input values
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)

    if (loggedIn) {
        return <Navigate to="/devices" replace/>
    }

    function handleSubmit(event) {
        event.preventDefault()   // no page reload: the request is sent with fetch
        setError(null)
        setLoading(true)
        login(email, password)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }

    return (
        <Card className="mx-auto" style={{maxWidth: 420}}>
            <Card.Body>
                <Card.Title className="mb-3">Accesso</Card.Title>
                {error && <Alert variant="danger">{error}</Alert>}
                <Form onSubmit={handleSubmit}>
                    <Form.Group className="mb-3" controlId="email">
                        <Form.Label>Email</Form.Label>
                        <Form.Control type="email" value={email} required
                                      onChange={e => setEmail(e.target.value)}/>
                    </Form.Group>
                    <Form.Group className="mb-3" controlId="password">
                        <Form.Label>Password</Form.Label>
                        <Form.Control type="password" value={password} required
                                      onChange={e => setPassword(e.target.value)}/>
                    </Form.Group>
                    <Button type="submit" disabled={loading} className="w-100">
                        {loading ? "Accesso in corso…" : "Accedi"}
                    </Button>
                </Form>
            </Card.Body>
        </Card>
    )
}
