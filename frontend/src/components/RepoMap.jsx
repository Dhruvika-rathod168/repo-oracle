import { useState } from "react"

export default function RepoMap({ chunks }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileSearch, setFileSearch]     = useState("")
  const [fnSearch, setFnSearch]         = useState("")

  // Build file → chunks map
  const fileMap = {}
  chunks.forEach(chunk => {
    const fp = chunk.file_path
    if (!fileMap[fp]) fileMap[fp] = []
    fileMap[fp].push(chunk)
  })

  const files = Object.keys(fileMap).sort()
  const filteredFiles = files.filter(fp =>
    fp.toLowerCase().includes(fileSearch.toLowerCase())
  )

  const selectedChunks = selectedFile
    ? fileMap[selectedFile].filter(c =>
        c.name.toLowerCase().includes(fnSearch.toLowerCase())
      )
    : []

  const getBasename = (fp) => fp.split(/[\\/]/).pop()

  return (
    <div style={{ flex: 1, display: "flex", gap: "16px", padding: "20px 24px", overflow: "hidden" }}>

      {/* Left — File Tree */}
      <div style={{
        width: "240px", minWidth: "240px",
        background: "#0d0d0d", border: "0.5px solid #1a1a1a",
        borderRadius: "12px", padding: "14px",
        display: "flex", flexDirection: "column", gap: "8px",
        overflowY: "auto"
      }}>
        <div style={{
          fontSize: "11px", color: "#666666", textTransform: "uppercase",
          letterSpacing: "0.08em", fontWeight: 500, marginBottom: "4px"
        }}>📂 File Tree</div>

        <input
          value={fileSearch}
          onChange={e => setFileSearch(e.target.value)}
          placeholder="🔍 Search files..."
          style={{
            background: "#000000", border: "0.5px solid #1a1a1a",
            borderRadius: "8px", padding: "7px 10px",
            color: "#ffffff", fontSize: "12px", outline: "none", width: "100%"
          }}
        />

        {filteredFiles.map(fp => (
          <button
            key={fp}
            onClick={() => { setSelectedFile(fp); setFnSearch("") }}
            style={{
              width: "100%", textAlign: "left",
              background: selectedFile === fp ? "#4c88db" : "#1a1a1a",
              border: "none", borderRadius: "8px",
              padding: "7px 10px", color: "#ffffff",
              fontSize: "12px", cursor: "pointer",
              transition: "background 0.15s"
            }}
          >
             {getBasename(fp)}
          </button>
        ))}
      </div>

      {/* Right — Function List */}
      <div style={{
        flex: 1, background: "#0d0d0d",
        border: "0.5px solid #1a1a1a", borderRadius: "12px",
        padding: "14px", display: "flex",
        flexDirection: "column", gap: "8px", overflowY: "auto"
      }}>
        {!selectedFile ? (
          <div style={{
            color: "#333333", fontSize: "13px",
            textAlign: "center", marginTop: "60px"
          }}>
            ← Select a file to see its functions and classes
          </div>
        ) : (
          <>
            <div style={{
              fontSize: "11px", color: "#666666", textTransform: "uppercase",
              letterSpacing: "0.08em", fontWeight: 500, marginBottom: "4px"
            }}>
              ⚡ Functions & Classes — {getBasename(selectedFile)}
            </div>

            <input
              value={fnSearch}
              onChange={e => setFnSearch(e.target.value)}
              placeholder="🔍 Search functions..."
              style={{
                background: "#000000", border: "0.5px solid #1a1a1a",
                borderRadius: "8px", padding: "7px 10px",
                color: "#ffffff", fontSize: "12px",
                outline: "none", width: "100%"
              }}
            />

            {selectedChunks.map((chunk, i) => (
              <div key={i} style={{
                background: "#000000", border: "0.5px solid #1a1a1a",
                borderRadius: "8px", padding: "10px 12px"
              }}>
                <div style={{ fontFamily: "monospace", fontSize: "13px", color: "#ffffff" }}>
                  {chunk.name}
                </div>
                <div style={{ display: "flex", gap: "8px", marginTop: "5px", alignItems: "center" }}>
                  <span style={{
                    fontSize: "10px", color: "#3351e8",
                    background: "#1a1a1a", padding: "2px 7px",
                    borderRadius: "10px"
                  }}>
                    {chunk.type}
                  </span>
                  <span style={{ fontSize: "11px", color: "#666666" }}>
                    line {chunk.start_line}–{chunk.end_line}
                  </span>
                </div>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  )
}