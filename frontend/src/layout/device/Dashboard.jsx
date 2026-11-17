import {Alert, Badge, Card, Col, Row} from "react-bootstrap"
import {Link} from "react-router-dom"

import {useAuth} from "../../context"
import {useSSE} from "../../hooks"
import {useDeviceList} from "./useDevice.js"

/**
 * Live dashboard: the device list is loaded once, then every SSE event
 * updates only the device it refers to.
 */
export function Dashboard() {
    const {token} = useAuth()
    const {list, setList, error} = useDeviceList(100)

    const {connected, error: streamError} = useSSE(token, ["telemetry", "status", "config"], (name, data) => {
        setList(prev => prev.map(device => {
            if (device.id !== data.device_id) return device
            switch (name) {
                case "telemetry":
                    return {...device, online: true, last_temperature: data.temperature, last_humidity: data.humidity}
                case "status":
                    return {...device, online: data.online, reported_version: data.reported_version,
                        in_sync: data.reported_version >= device.desired_version}
                case "config":
                    return {...device, desired_version: data.desired_version,
                        in_sync: device.reported_version >= data.desired_version}
                default:
                    return device
            }
        }))
    })

    return (
        <>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h2 className="h4 mb-0">Dashboard</h2>
                <Badge bg={connected ? "success" : "secondary"}>{connected ? "live" : "non connesso"}</Badge>
            </div>
            {error && <Alert variant="danger">{error}</Alert>}
            {streamError && <Alert variant="warning">{streamError}</Alert>}

            <Row xs={1} sm={2} lg={3} className="g-3">
                {list.map(device => (
                    <Col key={device.id}>
                        <DeviceCard device={device}/>
                    </Col>
                ))}
            </Row>
        </>
    )
}

function DeviceCard({device}) {
    const temperature = device.last_temperature ?? "—"
    return (
        <Card className="h-100">
            <Card.Body>
                <Card.Subtitle className="text-muted small">{device.site} · {device.serial}</Card.Subtitle>
                <Card.Title className="mt-1">{device.name}</Card.Title>
                <div className="display-6">{temperature} °C</div>
                <div className="text-muted small mb-2">Umidità {device.last_humidity ?? "—"} %</div>
                <Badge bg={device.online ? "success" : "secondary"} className="me-2">
                    {device.online ? "online" : "offline"}
                </Badge>
                {device.in_sync
                    ? <Badge bg="light" text="dark">config v{device.desired_version}</Badge>
                    : <Badge bg="warning">v{device.desired_version} in attesa</Badge>}
            </Card.Body>
            <Card.Footer className="bg-transparent">
                <Link to={`/devices/${device.id}/config`}>Configurazione</Link>
            </Card.Footer>
        </Card>
    )
}
