# SensorHub frontend

React + Vite, react-bootstrap. In development `/api` is proxied to the FastAPI backend on port 8000.

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # production files in dist/ (served by nginx, TW8)
```

Structure (one folder per area, one hooks file per resource):

```
src/
├── _services/fetchWrapper.js   # fetch + token + {success, message, data} envelope
├── context/AuthContext.jsx     # token, current user, login/logout
├── hooks/                      # generic hooks (useLocalStorage, useSSE)
└── layout/
    ├── Header.jsx, RequireAuth.jsx
    ├── account/Login.jsx
    └── device/useDevice.js, Devices.jsx, Dashboard.jsx, DeviceConfig.jsx
```
