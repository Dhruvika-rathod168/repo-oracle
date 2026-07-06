import { useState, useEffect } from "react"
import Login from "./components/Login"
import Sidebar from "./components/Sidebar"
import Chat from "./components/Chat"
import RepoMap from "./components/RepoMap"
import axios from "axios"

export default function App() {
  const [user, setUser]           = useState(null)
  const [repoInfo, setRepoInfo]   = useState(null)
  const [showMap, setShowMap]     = useState(false)
  const [chunks, setChunks]       = useState([])
  const [messages, setMessages]   = useState([])

  // Check if already logged in
  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      axios.get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setUser(res.data))
      .catch(() => localStorage.removeItem("token"))
    }
  }, [])

  // Set token on every axios request
  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`
    }
  }, [user])

  const handleLogin = (userData) => {
    setUser(userData)
    axios.defaults.headers.common["Authorization"] = `Bearer ${localStorage.getItem("token")}`
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    delete axios.defaults.headers.common["Authorization"]
    setUser(null)
    setRepoInfo(null)
    setMessages([])
    setChunks([])
  }

  if (!user) return <Login onLogin={handleLogin} />

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      <Sidebar
        repoInfo={repoInfo}
        setRepoInfo={setRepoInfo}
        setChunks={setChunks}
        showMap={showMap}
        setShowMap={setShowMap}
        user={user}
        onLogout={handleLogout}
      />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <div style={{ padding: "20px 24px 16px", borderBottom: "0.5px solid #1a1a1a" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <h1 style={{ fontSize: "22px", fontWeight: 600, color: "#ffffff" }}>
              Codebase Q&A Assistant
            </h1>
          </div>
          <p style={{ fontSize: "13px", color: "#666666", marginTop: "4px" }}>
            {!repoInfo
              ? "Index a repository to get started."
              : showMap
              ? "Browse the indexed files and functions below."
              : "✅ Repository indexed! View Repo Map or ask questions below."}
          </p>
        </div>

        <div style={{ display: showMap ? "none" : "flex", flex: 1, flexDirection: "column", overflow: "hidden" }}>
          <Chat repoInfo={repoInfo} messages={messages} setMessages={setMessages} />
        </div>
        <div style={{ display: showMap ? "flex" : "none", flex: 1, overflow: "hidden" }}>
          <RepoMap chunks={chunks} />
        </div>
      </div>
    </div>
  )
}