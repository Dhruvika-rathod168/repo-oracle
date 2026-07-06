import React from "react"
import ReactDOM from "react-dom/client"
import { GoogleOAuthProvider } from "@react-oauth/google"
import axios from "axios"
import App from "./App"
import "./index.css"

axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL || "https://repo-oracle-backend.onrender.com"

ReactDOM.createRoot(document.getElementById("root")).render(
  <GoogleOAuthProvider clientId="875120488650-o090od09eo16iketsidcb4kujji44v16.apps.googleusercontent.com">
    <App />
  </GoogleOAuthProvider>
)