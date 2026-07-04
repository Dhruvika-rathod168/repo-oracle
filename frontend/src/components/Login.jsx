import { useState } from "react"
import { GoogleLogin } from "@react-oauth/google"
import axios from "axios"

export default function Login({ onLogin }) {
  const [isSignup, setIsSignup]   = useState(false)
  const [name, setName]           = useState("")
  const [email, setEmail]         = useState("")
  const [password, setPassword]   = useState("")
  const [error, setError]         = useState("")
  const [loading, setLoading]     = useState(false)

  const handleSubmit = async () => {
    if (!email || !password) return
    setLoading(true)
    setError("")
    try {
      const endpoint = isSignup ? "/auth/signup" : "/auth/login"
      const body     = isSignup
        ? { email, name, password }
        : { email, password }
      const res = await axios.post(`http://localhost:8000${endpoint}`, body)
      localStorage.setItem("token", res.data.token)
      onLogin(res.data.user)
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const res = await axios.post("http://localhost:8000/auth/google", {
        token: credentialResponse.credential
      })
      localStorage.setItem("token", res.data.token)
      onLogin(res.data.user)
    } catch {
      setError("Google login failed. Try again.")
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit()
  }

  return (
    <div style={{
      height: "100vh", background: "#000000",
      display: "flex", alignItems: "center", justifyContent: "center"
    }}>
      <div style={{
        width: "400px", background: "#0d0d0d",
        border: "0.5px solid #1a1a1a", borderRadius: "16px",
        padding: "40px", display: "flex",
        flexDirection: "column", gap: "20px"
      }}>
        {/* Logo */}
        <div style={{ textAlign: "center" }}>
          <div style={{
            width: "48px", height: "48px", borderRadius: "12px",
            background: "linear-gradient(135deg, #1a1aff, #0099ff)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "22px", margin: "0 auto 12px"
          }}>⚡</div>
          <h1 style={{ fontSize: "20px", fontWeight: 600, color: "#ffffff" }}>
            CodebaseRAG
          </h1>
          <p style={{ fontSize: "13px", color: "#666666", marginTop: "4px" }}>
            {isSignup ? "Create your account" : "Welcome back"}
          </p>
        </div>

        {/* Google OAuth */}
        <div style={{ display: "flex", justifyContent: "center" }}>
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError("Google login failed")}
            theme="filled_black"
            shape="pill"
            text={isSignup ? "signup_with" : "signin_with"}
          />
        </div>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ flex: 1, height: "0.5px", background: "#1a1a1a" }} />
          <span style={{ fontSize: "12px", color: "#666666" }}>or</span>
          <div style={{ flex: 1, height: "0.5px", background: "#1a1a1a" }} />
        </div>

        {/* Name (signup only) */}
        {isSignup && (
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Full name"
            style={{
              background: "#000000", border: "0.5px solid #1a1a1a",
              borderRadius: "10px", padding: "11px 14px",
              color: "#ffffff", fontSize: "13px", outline: "none"
            }}
          />
        )}

        {/* Email */}
        <input
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Email address"
          type="email"
          onKeyDown={handleKeyDown}
          style={{
            background: "#000000", border: "0.5px solid #1a1a1a",
            borderRadius: "10px", padding: "11px 14px",
            color: "#ffffff", fontSize: "13px", outline: "none"
          }}
        />

        {/* Password */}
        <input
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          type="password"
          onKeyDown={handleKeyDown}
          style={{
            background: "#000000", border: "0.5px solid #1a1a1a",
            borderRadius: "10px", padding: "11px 14px",
            color: "#ffffff", fontSize: "13px", outline: "none"
          }}
        />

        {/* Error */}
        {error && (
          <div style={{
            fontSize: "12px", color: "#ff6b6b",
            background: "#1f0a0a", border: "0.5px solid #3d1a1a",
            borderRadius: "8px", padding: "8px 12px"
          }}>
            {error}
          </div>
        )}

        {/* Submit button */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            background: loading ? "#333" : "#4450f3",
            border: "none", borderRadius: "10px",
            padding: "12px", color: "#ffffff",
            fontSize: "14px", fontWeight: 500,
            cursor: loading ? "not-allowed" : "pointer"
          }}
        >
          {loading ? "Please wait..." : isSignup ? "Create Account" : "Sign In"}
        </button>

        {/* Toggle */}
        <p style={{ textAlign: "center", fontSize: "13px", color: "#666666" }}>
          {isSignup ? "Already have an account? " : "Don't have an account? "}
          <span
            onClick={() => { setIsSignup(!isSignup); setError("") }}
            style={{ color: "#4450f3", cursor: "pointer", fontWeight: 500 }}
          >
            {isSignup ? "Sign In" : "Sign Up"}
          </span>
        </p>
      </div>
    </div>
  )
}