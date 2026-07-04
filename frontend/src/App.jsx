import { useState } from "react"
import Sidebar from "./components/Sidebar"
import Chat from "./components/Chat"
import RepoMap from "./components/RepoMap"

export default function App() {
  const [repoInfo, setRepoInfo]   = useState(null)
  const [showMap, setShowMap]     = useState(false)
  const [chunks, setChunks]       = useState([])
  const [messages, setMessages]   = useState([])


  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden" }}>
      {/* Sidebar */}
      <Sidebar
        repoInfo={repoInfo}
        setRepoInfo={setRepoInfo}
        setChunks={setChunks}
        showMap={showMap}
        setShowMap={setShowMap}
      />

      {/* Main area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Header */}
        <div style={{
          padding: "20px 24px 16px",
          borderBottom: "0.5px solid #1a1a1a",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <h1 style={{ fontSize: "22px", fontWeight: 600, color: "#ffffff" }}>
              Codebase Q&A Assistant
            </h1>
          </div>
          <p style={{ fontSize: "13px", color: "#666666", marginTop: "4px" }}>
            {!repoInfo
              ? "Index a repository to access repo map."
              : showMap
              ? "Browse the indexed files and functions below."
              : "View Repo Map or ask questions below."}
          </p>
        </div>

        {/* Content */}
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