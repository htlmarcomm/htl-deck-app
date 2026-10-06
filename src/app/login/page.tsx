"use client";

import { useState } from "react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const r = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (r.ok) {
        window.location.href = "/";
        return;
      }
      const j = await r.json().catch(() => ({}));
      setError(j.error || "Could not sign in.");
    } catch {
      setError("Network problem - try again.");
    }
    setBusy(false);
  }

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#f4f3ef", fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif", color: "#14140f" }}>
      <form onSubmit={submit} style={{ width: 340, background: "#fff", border: "1px solid rgba(20,19,15,.12)", borderRadius: 16, padding: 28, boxShadow: "0 8px 24px -12px rgba(20,19,15,.25)" }}>
        <div style={{ fontWeight: 700, fontSize: 18, marginBottom: 4 }}>
          HTL <span style={{ color: "#e5222a" }}>Deck Platform</span>
        </div>
        <p style={{ margin: "0 0 20px", fontSize: 13, color: "#6b6a63" }}>Sign in to build and share decks.</p>
        <label style={{ display: "block", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".05em", color: "#6b6a63", marginBottom: 4 }}>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" autoFocus style={inp} />
        <label style={{ display: "block", fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: ".05em", color: "#6b6a63", margin: "14px 0 4px" }}>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" style={inp} />
        {error && <p style={{ color: "#e5222a", fontSize: 13, margin: "12px 0 0" }}>{error}</p>}
        <button disabled={busy} style={{ marginTop: 20, width: "100%", padding: "11px 0", border: 0, borderRadius: 10, background: "#e5222a", color: "#fff", fontWeight: 600, fontSize: 14, cursor: "pointer", opacity: busy ? 0.6 : 1 }}>
          {busy ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}

const inp: React.CSSProperties = { width: "100%", boxSizing: "border-box", padding: "10px 12px", border: "1px solid rgba(20,19,15,.22)", borderRadius: 8, fontSize: 14 };
