import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("owner@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <main className="page narrow">
      <section className="card">
        <h1>Login</h1>
        <p className="muted">Demo users use password <strong>password123</strong>.</p>
        {error && <p className="error">{error}</p>}
        <form onSubmit={handleSubmit} className="stack">
          <label>Email
            <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
          </label>
          <label>Password
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
          </label>
          <button type="submit">Login</button>
        </form>
        <p className="muted">Need an invite? <Link to="/register">Register with an invite token</Link>.</p>
      </section>
    </main>
  );
}
