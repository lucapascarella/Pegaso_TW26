import {Alert, Badge, Button, Pagination, Spinner, Table} from "react-bootstrap"

import {useDeviceCount, useDeviceList} from "./useDevice.js"

const PAGE_SIZE = 10

export function Devices() {
    const {list, loading, error, pageIndex, setPageIndex, reload} = useDeviceList(PAGE_SIZE)
    const count = useDeviceCount()
    const pages = Math.max(1, Math.ceil(count / PAGE_SIZE))

    return (
        <>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h2 className="h4 mb-0">Device ({count})</h2>
                <Button size="sm" variant="outline-secondary" onClick={reload}>Aggiorna</Button>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}
            {loading && <Spinner animation="border" size="sm"/>}

            <Table hover responsive>
                <thead>
                <tr>
                    <th>Seriale</th>
                    <th>Nome</th>
                    <th>Serra</th>
                    <th>Tipo</th>
                    <th>Stato</th>
                    <th>Configurazione</th>
                </tr>
                </thead>
                <tbody>
                {list.map(device => (
                    <tr key={device.id}>
                        <td><code>{device.serial}</code></td>
                        <td>{device.name}</td>
                        <td>{device.site}</td>
                        <td>{device.device_class}</td>
                        <td>
                            <Badge bg={device.online ? "success" : "secondary"}>
                                {device.online ? "online" : "offline"}
                            </Badge>
                        </td>
                        <td>
                            {device.in_sync
                                ? <Badge bg="light" text="dark">v{device.desired_version}</Badge>
                                : <Badge bg="warning">v{device.desired_version} in attesa</Badge>}
                        </td>
                    </tr>
                ))}
                </tbody>
            </Table>

            <Pagination>
                {Array.from({length: pages}, (_, i) => (
                    <Pagination.Item key={i} active={i === pageIndex} onClick={() => setPageIndex(i)}>
                        {i + 1}
                    </Pagination.Item>
                ))}
            </Pagination>
        </>
    )
}
