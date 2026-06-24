import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../api/client";
import type { Reservation, Tool } from "../types";

export default function BrowseToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [selectedToolId, setSelectedToolId] = useState<number | null>(null);
  const [startDate, setStartDate] = useState("2026-08-01");
  const [endDate, setEndDate] = useState("2026-08-02");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function loadTools() {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (category) params.set("category", category);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    const results = await apiFetch<Tool[]>(`/tools${suffix}`);
    setTools(results);
  }

  useEffect(() => {
    void loadTools().catch((err) => setError(err instanceof Error ? err.message : "Could not load tools"));
  }, []);

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    setError("");
    await loadTools().catch((err) => setError(err instanceof Error ? err.message : "Search failed"));
  }

  async function requestReservation(toolId: number) {
    setError("");
    setMessage("");
    try {
      const reservation = await apiFetch<Reservation>("/reservations", {
        method: "POST",
        body: JSON.stringify({ tool_id: toolId, start_date: startDate, end_date: endDate })
      });
      setSelectedToolId(null);
      setMessage(`Reservation #${reservation.id} requested.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not request reservation");
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <h1>Browse tools</h1>
          <p>Search active community listings and request a reservation date range.</p>
        </div>
      </section>

      <form className="card inline-form" onSubmit={handleSearch}>
        <label>Keyword
          <input value={q} onChange={(event) => setQ(event.target.value)} placeholder="drill, ladder, rake" />
        </label>
        <label>Category
          <input value={category} onChange={(event) => setCategory(event.target.value)} placeholder="Power Tools" />
        </label>
        <button type="submit">Search</button>
      </form>

      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <section className="tool-grid">
        {tools.map((tool) => (
          <article className="card tool-card" key={tool.id}>
            {tool.photo_url && <img src={tool.photo_url} alt="" />}
            <h2>{tool.name}</h2>
            <p>{tool.description}</p>
            <p><strong>Category:</strong> {tool.category}</p>
            <p><strong>Condition:</strong> {tool.condition}</p>
            {tool.lending_rules && <p><strong>Rules:</strong> {tool.lending_rules}</p>}
            <div className="actions">
              <Link className="button secondary" to={`/tools/${tool.id}`}>Details</Link>
              <button onClick={() => setSelectedToolId(selectedToolId === tool.id ? null : tool.id)}>Request</button>
            </div>
            {selectedToolId === tool.id && (
              <div className="request-box">
                <label>Start date<input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label>
                <label>End date<input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label>
                <button onClick={() => void requestReservation(tool.id)}>Submit request</button>
              </div>
            )}
          </article>
        ))}
      </section>
    </main>
  );
}
