import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("New Neighbor");
  const [email, setEmail] = useState("newneighbor@example.com");
  const [password, setPassword] = useState("password123");
  const [inviteToken, setInviteToken] = useState("DEMO-INVITE-NEW");
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await register(fullName, email, password, inviteToken);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    }
  }

  return (
    <main className="page narrow">
      <section className="card">
        <h1>Invite-only registration</h1>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit} className="stack">
          <label>Full name
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} required />
          </label>
          <label>Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label>Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" minLength={8} required />
          </label>
          <label>Invite token
            <input value={inviteToken} onChange={(event) => setInviteToken(event.target.value)} required />
          </label>
          <button type="submit">Create account</button>
        </form>
      </section>
    </main>
  );
}
