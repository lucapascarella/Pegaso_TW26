import {Navigate, Route, Routes} from "react-router-dom"
import {Container} from "react-bootstrap"

import {Header} from "./layout/Header.jsx"
import {RequireAuth} from "./layout/RequireAuth.jsx"
import {Login} from "./layout/account/Login.jsx"
import {Dashboard} from "./layout/device/Dashboard.jsx"
import {DeviceConfig} from "./layout/device/DeviceConfig.jsx"
import {Devices} from "./layout/device/Devices.jsx"

export default function App() {
    return (
        <>
            <Header/>
            <Container className="py-4">
                <Routes>
                    <Route path="/login" element={<Login/>}/>
                    <Route path="/dashboard" element={<RequireAuth><Dashboard/></RequireAuth>}/>
                    <Route path="/devices" element={<RequireAuth><Devices/></RequireAuth>}/>
                    <Route path="/devices/:deviceId/config" element={<RequireAuth><DeviceConfig/></RequireAuth>}/>
                    <Route path="*" element={<Navigate to="/dashboard" replace/>}/>
                </Routes>
            </Container>
        </>
    )
}
