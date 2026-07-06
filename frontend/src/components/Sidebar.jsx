import { useState } from "react"
import axios from "axios"

export default function Sidebar({ repoInfo, setRepoInfo, setChunks, showMap, setShowMap, user, onLogout }) {
  const [repoUrl, setRepoUrl] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState("")
  const [success, setSuccess]   = useState(false)

  const handleIndex = async () => {
    if (!repoUrl.trim()) return
    setLoading(true)
    setError("")
    try {
      const res = await axios.post("/index", {
        repo_url: repoUrl.trim()
      })
      setRepoInfo(res.data)

      // fetch repo map chunks
      const mapRes = await axios.get("/repomap")
      setChunks(mapRes.data.chunks)
      setSuccess(true)
    } catch (err) {
      setError("Failed to index repository. Check the URL and try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      width: "260px", minWidth: "260px",
      background: "#000000",
      borderRight: "0.5px solid #1a1a1a",
      padding: "24px 18px",
      display: "flex", flexDirection: "column", gap: "20px",
      overflowY: "auto"
    }}>
      {/* Brand */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <div style={{
          width: "26px", height: "26px", borderRadius: "8px",
          background: "linear-gradient(135deg, #1a1aff, #0099ff)",
          display: "flex", alignItems: "center",
          justifyContent: "center", fontSize: "13px"
        }}>⚡</div>
        <span style={{ fontSize: "16px", fontWeight: 500, color: "#ffffff" }}>
          Repo-Oracle
        </span>
      </div>

      <div style={{ height: "0.5px", background: "#1a1a1a" }} />

      {/* Repo URL input */}
      <div>
        <div style={{
          fontSize: "11px", color: "#f3f3f3", textTransform: "uppercase",
          letterSpacing: "0.08em", fontWeight: 500, marginBottom: "8px"
        }}>Repository</div>

        <div style={{ fontSize: "12px", color: "#666666", marginBottom: "6px" }}>
          GitHub repo URL
        </div>

        <input
          value={repoUrl}
          onChange={e => setRepoUrl(e.target.value)}
          placeholder="https://github.com/user/repo"
          style={{
            width: "100%", background: "#0d0d0d",
            border: "0.5px solid #1a1a1a", borderRadius: "10px",
            padding: "10px 12px", color: "#ffffff",
            fontSize: "12px", outline: "none",
            marginBottom: "10px"
          }}
        />

        <button
          onClick={handleIndex}
          disabled={loading}
          style={{
            width: "100%", background: loading ? "#333" : "#4c88db",
            border: "none", borderRadius: "10px",
            padding: "10px", color: "#ffffff",
            fontSize: "13px", fontWeight: 500,
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "Indexing..." : "⚡ Index Repository"}
        </button>

        {error && (
  <div style={{ fontSize: "12px", color: "#ff6b6b", marginTop: "8px" }}>
    {error}
  </div>
)}
{success && (
  <div style={{ fontSize: "12px", color: "#4ade80", marginTop: "8px",
                background: "#0a1f12", border: "0.5px solid #1a3d28",
                borderRadius: "8px", padding: "7px 10px" }}>
    ✓ Indexed successfully!
  </div>
)}

      </div>

      {/* Repo info card */}
      {repoInfo && (
        <>
          <div style={{
            background: "#0d0d0d", border: "0.5px solid #1a1a1a",
            borderRadius: "10px", padding: "12px"
          }}>
            <div style={{ fontSize: "13px", color: "#ffffff", fontWeight: 500 }}>
              {repoInfo.repo_name}
            </div>
            <div style={{ fontSize: "11px", color: "#666666", marginTop: "4px" }}>
              Python · indexed
            </div>
            <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
              <span style={{
                fontSize: "11px", color: "#ffffff", background: "#1a1a1a",
                padding: "3px 8px", borderRadius: "20px",
                border: "0.5px solid #333333"
              }}>
                {repoInfo.chunks} chunks
              </span>
              <span style={{
                fontSize: "11px", color: "#ffffff", background: "#1a1a1a",
                padding: "3px 8px", borderRadius: "20px",
                border: "0.5px solid #333333"
              }}>
                {repoInfo.files} files
              </span>
            </div>
          </div>

          {/* Map / Chat toggle button */}
          <button
            onClick={() => setShowMap(!showMap)}
            style={{
              width: "100%", background: "#0d0d0d",
              border: "0.5px solid #1a1a1a", borderRadius: "10px",
              padding: "10px", color: "#ffffff",
              fontSize: "13px", fontWeight: 500, cursor: "pointer"
            }}
          >
            {showMap ? "💬 Back to Chat" : "🗺️ View Repo Map"}
          </button>
        </>
      )}

      {/* User profile */}
      <div style={{ marginTop: "auto", paddingTop: "16px", borderTop: "0.5px solid #1a1a1a" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
          {user.avatar_url
            ? <img src={user.avatar_url} style={{ width: "32px", height: "32px", borderRadius: "50%" }} />
            : <div style={{
                width: "32px", height: "32px", borderRadius: "50%",
                background: "#7c6fff", display: "flex", alignItems: "center",
                justifyContent: "center", fontSize: "13px", fontWeight: 500
              }}>{user.name?.[0] || user.email?.[0]}</div>
          }
          <div>
            <div style={{ fontSize: "13px", color: "#ffffff", fontWeight: 500 }}>
              {user.name || "User"}
            </div>
            <div style={{ fontSize: "11px", color: "#666666" }}>{user.email}</div>
          </div>
        </div>
        <button
          onClick={onLogout}
          onMouseEnter={e => {
            e.target.style.background = "#4c88db"
            e.target.style.color = "#ffffff"
            e.target.style.border = "0.5px solid #4c88db"
          }}
          onMouseLeave={e => {
            e.target.style.background = "#0d0d0d"
            e.target.style.color = "#666666"
            e.target.style.border = "0.5px solid #1a1a1a"
          }}
          style={{
            width: "100%", background: "#0d0d0d",
            border: "0.5px solid #1a1a1a", borderRadius: "10px",
            padding: "8px", color: "#666666",
            fontSize: "12px", cursor: "pointer",
            transition: "all 0.2s"
          }}
        >
          Sign Out
        </button>
      </div>

    </div>
  )
}