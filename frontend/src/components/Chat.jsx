import { useState, useRef, useEffect } from "react"
import axios from "axios"

export default function Chat({ repoInfo, messages, setMessages }) {
  const [question, setQuestion]   = useState("")
  const [loading, setLoading]     = useState(false)
  const [agentMode, setAgentMode] = useState(false)
  const bottomRef                 = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const handleAsk = async () => {
    if (!question.trim() || !repoInfo) return
    const userMsg = { role: "user", content: question }
    setMessages(prev => [...prev, userMsg])
    setQuestion("")
    setLoading(true)

    try {
      const endpoint = agentMode ? "/ask-agent" : "/ask"
      const res = await axios.post(`https://repo-oracle-backend.onrender.com${endpoint}`, {
        question: userMsg.content
      })
      setMessages(prev => [...prev, { role: "assistant", content: res.data.answer }])
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "❌ Error getting answer. Make sure the backend is running."
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleAsk()
    }
  }

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

      {/* Messages */}
      <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px", display: "flex", flexDirection: "column", gap: "16px" }}>
        {messages.length === 0 && (
          <div style={{ textAlign: "center", color: "#333333", marginTop: "60px", fontSize: "14px" }}>
            {repoInfo
              ? "Ask a question about the indexed codebase"
              : "Index a repository first, then ask questions here"}
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex", gap: "10px",
            flexDirection: msg.role === "user" ? "row-reverse" : "row",
            alignItems: "flex-start"
          }}>
            <div style={{
              width: "30px", height: "30px", borderRadius: "50%",
              background: "#0d0d0d", border: "0.5px solid #1a1a1a",
              display: "flex", alignItems: "center",
              justifyContent: "center", fontSize: "12px", flexShrink: 0
            }}>
              {msg.role === "user" ? "👤" : "⚡"}
            </div>
            <div style={{
              maxWidth: "72%", padding: "11px 15px",
              borderRadius: "14px", fontSize: "13px", lineHeight: "1.65",
              background: msg.role === "user" ? "#4450f3" : "#0d0d0d",
              color: "#ffffff",
              border: msg.role === "user" ? "none" : "0.5px solid #1a1a1a",
              borderTopRightRadius: msg.role === "user" ? "4px" : "14px",
              borderTopLeftRadius: msg.role === "assistant" ? "4px" : "14px",
              whiteSpace: "pre-wrap"
            }}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
            <div style={{
              width: "30px", height: "30px", borderRadius: "50%",
              background: "#0d0d0d", border: "0.5px solid #1a1a1a",
              display: "flex", alignItems: "center", justifyContent: "center"
            }}>⚡</div>
            <div style={{
              padding: "11px 15px", borderRadius: "14px",
              background: "#0d0d0d", border: "0.5px solid #1a1a1a",
              fontSize: "13px", color: "#666666"
            }}>
              {agentMode ? "🤖 Agent is thinking..." : "Thinking..."}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div style={{ padding: "16px 24px", borderTop: "0.5px solid #1a1a1a" }}>

        {/* Mode toggle */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
          <span style={{ fontSize: "12px", color: "#666666" }}>Mode:</span>
          <button
            onClick={() => setAgentMode(false)}
            style={{
              fontSize: "11px", padding: "3px 10px", borderRadius: "20px",
              border: "none", cursor: "pointer",
              background: !agentMode ? "#4c88db" : "#1a1a1a",
              color: !agentMode ? "#ffffff" : "#666666"
            }}
          >Traditional</button>
          <button
            onClick={() => setAgentMode(true)}
            style={{
              fontSize: "11px", padding: "3px 10px", borderRadius: "20px",
              border: "none", cursor: "pointer",
              background: agentMode ? "#4c88db" : "#1a1a1a",
              color: agentMode ? "#ffffff" : "#666666"
            }}
          >⚡ Agentic</button>
        </div>

        {/* Input row */}
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <input
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={repoInfo ? "Ask a question about the indexed codebase..." : "Index a repository first..."}
            disabled={!repoInfo || loading}
            style={{
              flex: 1, background: "#0d0d0d",
              border: "0.5px solid #1a1a1a", borderRadius: "24px",
              padding: "11px 18px", color: "#ffffff",
              fontSize: "13px", outline: "none",
              opacity: !repoInfo ? 0.5 : 1
            }}
          />
          <button
            onClick={handleAsk}
            disabled={!repoInfo || loading || !question.trim()}
            style={{
              width: "38px", height: "38px", borderRadius: "50%",
              background: !repoInfo || loading ? "#333" : agentMode ? "#4c88db" : "#4450f3",
              border: "none", color: "#ffffff",
              fontSize: "16px", cursor: !repoInfo || loading ? "not-allowed" : "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0
            }}
          >↑</button>
        </div>
      </div>
    </div>
  )
}