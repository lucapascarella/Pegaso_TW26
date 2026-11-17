import {defineConfig} from "vite"
import react from "@vitejs/plugin-react"

// In development the React app runs on :5173 and the API on :8000.
// The proxy forwards /api to FastAPI: for the browser everything comes from the same origin (no CORS needed).
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            "/api": "http://127.0.0.1:8000",
        },
    },
})
