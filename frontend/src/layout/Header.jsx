import {Badge, Button, Container, Nav, Navbar} from "react-bootstrap"
import {Link} from "react-router-dom"

import {useAuth} from "../context"

export function Header() {
    const {loggedIn, user, logout} = useAuth()

    return (
        <Navbar bg="dark" data-bs-theme="dark" expand="sm">
            <Container>
                <Navbar.Brand as={Link} to="/">SensorHub</Navbar.Brand>
                {loggedIn && (
                    <>
                        <Nav className="me-auto">
                            <Nav.Link as={Link} to="/dashboard">Dashboard</Nav.Link>
                            <Nav.Link as={Link} to="/devices">Device</Nav.Link>
                        </Nav>
                        <Navbar.Text className="me-3">
                            {user.full_name} <Badge bg="secondary">{user.role}</Badge>
                        </Navbar.Text>
                        <Button size="sm" variant="outline-light" onClick={logout}>Esci</Button>
                    </>
                )}
            </Container>
        </Navbar>
    )
}
