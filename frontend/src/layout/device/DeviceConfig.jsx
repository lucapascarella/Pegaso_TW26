import {useState} from "react"
import {Alert, Button, Card, Col, Form, Row, Spinner} from "react-bootstrap"
import {Link, useParams} from "react-router-dom"
import {Formik} from "formik"
import * as yup from "yup"

import {useAuth} from "../../context"
import {useDeviceConfig} from "./useDevice.js"

// Same rules as the backend (ReqConfigUpdate): the backend still validates, the UI only helps the user
const validationSchema = yup.object().shape({
    min_temp: yup.number().required("Campo obbligatorio").min(-20).max(60),
    max_temp: yup.number().required("Campo obbligatorio").min(-20).max(60)
        .moreThan(yup.ref("min_temp"), "Deve essere maggiore della minima"),
    sampling_sec: yup.number().required("Campo obbligatorio").integer().min(5).max(3600),
})

export function DeviceConfig() {
    const {deviceId} = useParams()
    const {canEdit} = useAuth()
    const {device, config, loading, error, saveConfig, reload} = useDeviceConfig(deviceId)
    const [message, setMessage] = useState(null)

    if (loading || !config) {
        return error ? <Alert variant="danger">{error}</Alert> : <Spinner animation="border"/>
    }

    function handleSubmit(values, {setSubmitting}) {
        setMessage(null)
        // The version read with the form is sent back: optimistic locking (TW2)
        saveConfig({...values, version: config.version})
            .then(msg => setMessage({variant: "success", text: msg}))
            .catch(err => {
                if (err.status === 409) {
                    setMessage({variant: "warning", text: "Un altro utente ha modificato la configurazione: valori ricaricati."})
                    reload()
                } else {
                    setMessage({variant: "danger", text: err.message})
                }
            })
            .finally(() => setSubmitting(false))
    }

    return (
        <Card className="mx-auto" style={{maxWidth: 560}}>
            <Card.Body>
                <Card.Title>{device.name}</Card.Title>
                <Card.Subtitle className="text-muted mb-3">
                    Configurazione v{config.version}
                    {!device.in_sync && " · non ancora applicata dal device"}
                </Card.Subtitle>
                {message && <Alert variant={message.variant}>{message.text}</Alert>}
                {!canEdit && <Alert variant="info">Accesso in sola lettura.</Alert>}

                <Formik initialValues={{min_temp: config.min_temp, max_temp: config.max_temp, sampling_sec: config.sampling_sec}}
                        enableReinitialize validationSchema={validationSchema} onSubmit={handleSubmit}>
                    {({handleSubmit, handleChange, values, errors, touched, isSubmitting}) => (
                        <Form noValidate onSubmit={handleSubmit}>
                            <Row>
                                <Col sm={6}>
                                    <NumberField name="min_temp" label="Temperatura minima (°C)" values={values}
                                                 errors={errors} touched={touched} onChange={handleChange} disabled={!canEdit}/>
                                </Col>
                                <Col sm={6}>
                                    <NumberField name="max_temp" label="Temperatura massima (°C)" values={values}
                                                 errors={errors} touched={touched} onChange={handleChange} disabled={!canEdit}/>
                                </Col>
                            </Row>
                            <NumberField name="sampling_sec" label="Campionamento (s)" values={values}
                                         errors={errors} touched={touched} onChange={handleChange} disabled={!canEdit}/>
                            <div className="d-flex justify-content-between">
                                <Link to="/dashboard" className="btn btn-outline-secondary">Indietro</Link>
                                {/* Hiding the button is only a UI choice: the backend answers 403 anyway */}
                                {canEdit && <Button type="submit" disabled={isSubmitting}>Salva</Button>}
                            </div>
                        </Form>
                    )}
                </Formik>
            </Card.Body>
        </Card>
    )
}

function NumberField({name, label, values, errors, touched, onChange, disabled}) {
    return (
        <Form.Group className="mb-3" controlId={name}>
            <Form.Label>{label}</Form.Label>
            <Form.Control type="number" step="any" name={name} value={values[name]} onChange={onChange}
                          disabled={disabled} isInvalid={touched[name] && !!errors[name]}/>
            <Form.Control.Feedback type="invalid">{errors[name]}</Form.Control.Feedback>
        </Form.Group>
    )
}
