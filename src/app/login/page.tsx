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
    <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#f9fafb", fontFamily: font, color: "#111827" }}>
      <form onSubmit={submit} style={{ width: "100%", maxWidth: 384, background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, padding: 32, boxShadow: "0 1px 2px 0 rgba(0,0,0,.05)", boxSizing: "border-box" }}>
        <h1 style={{ margin: "0 0 4px", fontSize: 20, fontWeight: 700 }}>HTL Deck Platform</h1>
        <p style={{ margin: "0 0 24px", fontSize: 14, color: "#6b7280" }}>Sign in to continue</p>
        {error && (
          <div style={{ marginBottom: 16, fontSize: 14, color: "#b91c1c", background: "#fef2f2", border: "1px solid #fee2e2", borderRadius: 8, padding: "8px 12px" }}>{error}</div>
        )}
        <label style={lbl}>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" autoFocus required style={{ ...inp, marginBottom: 16 }} />
        <label style={lbl}>Password</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required style={{ ...inp, marginBottom: 24 }} />
        <button
          disabled={busy}
          onMouseOver={(e) => (e.currentTarget.style.background = "#dc2626")}
          onMouseOut={(e) => (e.currentTarget.style.background = "#111827")}
          style={{ width: "100%", padding: "9px 16px", border: 0, borderRadius: 8, background: "#111827", color: "#fff", fontWeight: 500, fontSize: 14, fontFamily: font, cursor: busy ? "default" : "pointer", opacity: busy ? 0.5 : 1, transition: "background .15s" }}
        >
          {busy ? "Signing in..." : "Sign in"}
        </button>
      </form>
    </main>
  );
}

const font = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
const lbl: React.CSSProperties = { display: "block", fontSize: 12, fontWeight: 500, color: "#4b5563", marginBottom: 4 };
const inp: React.CSSProperties = { width: "100%", boxSizing: "border-box", padding: "8px 12px", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 14, fontFamily: font, background: "#fff" };
