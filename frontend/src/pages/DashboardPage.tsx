import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import type { Dashboard } from "../types";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Dashboard>("/users/me/dashboard")
      .then(setDashboard)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load dashboard"));
  }, []);

  if (error) return <main className="page"><p className="error">{error}</p></main>;
  if (!dashboard) return <main className="page"><p>Loading dashboard...</p></main>;

  return (
    <main className="page">
      <section className="hero">
        <div>
          <h1>Welcome, {dashboard.profile.full_name}</h1>
          <p>Manage tools, requests, reservations, messages, and reviews from one place.</p>
        </div>
        <Link className="button" to="/tools">Browse tools</Link>
      </section>

      <section className="grid three">
        <article className="card metric"><span>{dashboard.my_tools.length}</span><p>My tool listings</p></article>
        <article className="card metric"><span>{dashboard.incoming_requests.length}</span><p>Incoming requests</p></article>
        <article className="card metric"><span>{dashboard.outgoing_reservations.length}</span><p>Outgoing reservations</p></article>
      </section>

      <section className="grid two">
        <article className="card">
          <h2>Unread notifications</h2>
          {dashboard.unread_notifications.length === 0 ? <p className="muted">No unread notifications.</p> : (
            <ul className="clean-list">
              {dashboard.unread_notifications.map((item) => (
                <li key={item.id}>
                  <strong>{item.title}</strong>
                  <p>{item.body}</p>
                </li>
              ))}
            </ul>
          )}
        </article>
        <article className="card">
          <h2>Open incoming requests</h2>
          <ul className="clean-list">
            {dashboard.incoming_requests.slice(0, 5).map((reservation) => (
              <li key={reservation.id}>
                <strong>{reservation.tool?.name ?? `Tool #${reservation.tool_id}`}</strong>
                <p>{reservation.status}: {reservation.start_date} to {reservation.end_date}</p>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </main>
  );
}
