import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { apiFetch } from "../api/client";
import type { Reservation, Tool } from "../types";

interface AvailabilityWindow {
  reservation_id: number;
  start_date: string;
  end_date: string;
  status: string;
}

export default function ToolDetailsPage() {
  const { toolId } = useParams();
  const [tool, setTool] = useState<Tool | null>(null);
  const [availability, setAvailability] = useState<AvailabilityWindow[]>([]);
  const [startDate, setStartDate] = useState("2026-08-01");
  const [endDate, setEndDate] = useState("2026-08-02");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!toolId) return;
    Promise.all([
      apiFetch<Tool>(`/tools/${toolId}`),
      apiFetch<AvailabilityWindow[]>(`/tools/${toolId}/availability`)
    ])
      .then(([toolData, availabilityData]) => {
        setTool(toolData);
        setAvailability(availabilityData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load tool"));
  }, [toolId]);

  async function requestReservation(event: FormEvent) {
    event.preventDefault();
    if (!tool) return;
    setMessage("");
    setError("");
    try {
      const reservation = await apiFetch<Reservation>("/reservations", {
        method: "POST",
        body: JSON.stringify({ tool_id: tool.id, start_date: startDate, end_date: endDate })
      });
      setMessage(`Reservation #${reservation.id} requested.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    }
  }

  if (error) return <main className="page"><p className="error">{error}</p></main>;
  if (!tool) return <main className="page"><p>Loading tool...</p></main>;

  return (
    <main className="page">
      <section className="card detail-card">
        {tool.photo_url && <img src={tool.photo_url} alt="" />}
        <div>
          <h1>{tool.name}</h1>
          <p>{tool.description}</p>
          <p><strong>Owner:</strong> {tool.owner?.full_name ?? `User #${tool.owner_id}`}</p>
          <p><strong>Category:</strong> {tool.category}</p>
          <p><strong>Condition:</strong> {tool.condition}</p>
          <p><strong>Lending rules:</strong> {tool.lending_rules ?? "No special rules."}</p>
        </div>
      </section>

      {message && <p className="success">{message}</p>}

      <section className="grid two">
        <form className="card stack" onSubmit={requestReservation}>
          <h2>Request reservation</h2>
          <label>Start date<input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></label>
          <label>End date<input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></label>
          <button type="submit">Submit request</button>
        </form>
        <article className="card">
          <h2>Unavailable windows</h2>
          {availability.length === 0 ? <p className="muted">No approved or picked-up reservations.</p> : (
            <ul className="clean-list">
              {availability.map((item) => (
                <li key={item.reservation_id}>{item.start_date} to {item.end_date} - {item.status}</li>
              ))}
            </ul>
          )}
        </article>
      </section>
    </main>
  );
}
