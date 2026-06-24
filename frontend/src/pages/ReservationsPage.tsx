import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import type { Message, Reservation } from "../types";

export default function ReservationsPage() {
  const [incoming, setIncoming] = useState<Reservation[]>([]);
  const [outgoing, setOutgoing] = useState<Reservation[]>([]);
  const [selected, setSelected] = useState<Reservation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [body, setBody] = useState("");
  const [reviewComment, setReviewComment] = useState("Great experience.");
  const [damageDescription, setDamageDescription] = useState("Small scratch noticed during return.");
  const [error, setError] = useState("");

  async function loadReservations() {
    const [incomingRows, outgoingRows] = await Promise.all([
      apiFetch<Reservation[]>("/reservations/incoming"),
      apiFetch<Reservation[]>("/reservations/outgoing")
    ]);
    setIncoming(incomingRows);
    setOutgoing(outgoingRows);
  }

  async function loadMessages(reservation: Reservation) {
    setSelected(reservation);
    setMessages(await apiFetch<Message[]>(`/messages/${reservation.id}`));
  }

  useEffect(() => {
    void loadReservations().catch((err) => setError(err instanceof Error ? err.message : "Could not load reservations"));
  }, []);

  async function runAction(reservation: Reservation, action: "approve" | "deny" | "cancel" | "pickup" | "return") {
    setError("");
    try {
      await apiFetch<Reservation>(`/reservations/${reservation.id}/${action}`, { method: "POST" });
      await loadReservations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    }
  }

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    await apiFetch<Message>(`/messages/${selected.id}`, { method: "POST", body: JSON.stringify({ body }) });
    setBody("");
    await loadMessages(selected);
  }

  async function submitReview() {
    if (!selected) return;
    await apiFetch(`/reviews/${selected.id}`, {
      method: "POST",
      body: JSON.stringify({ rating: 5, comment: reviewComment })
    });
    setReviewComment("Great experience.");
  }

  async function submitDamageReport() {
    if (!selected) return;
    await apiFetch(`/damage-reports/${selected.id}`, {
      method: "POST",
      body: JSON.stringify({ description: damageDescription, photo_url: null })
    });
    setDamageDescription("Small scratch noticed during return.");
  }

  function reservationCard(reservation: Reservation, mode: "incoming" | "outgoing") {
    return (
      <article className="card" key={`${mode}-${reservation.id}`}>
        <h3>{reservation.tool?.name ?? `Tool #${reservation.tool_id}`}</h3>
        <p><strong>Status:</strong> {reservation.status}</p>
        <p>{reservation.start_date} to {reservation.end_date}</p>
        <div className="actions wrap">
          {mode === "incoming" && reservation.status === "REQUESTED" && <button onClick={() => void runAction(reservation, "approve")}>Approve</button>}
          {mode === "incoming" && reservation.status === "REQUESTED" && <button onClick={() => void runAction(reservation, "deny")}>Deny</button>}
          {mode === "incoming" && reservation.status === "PICKED_UP" && <button onClick={() => void runAction(reservation, "return")}>Confirm returned</button>}
          {mode === "outgoing" && reservation.status === "APPROVED" && <button onClick={() => void runAction(reservation, "pickup")}>Mark picked up</button>}
          {(reservation.status === "REQUESTED" || reservation.status === "APPROVED") && <button onClick={() => void runAction(reservation, "cancel")}>Cancel</button>}
          <button className="secondary" onClick={() => void loadMessages(reservation)}>Messages / Review</button>
        </div>
      </article>
    );
  }

  return (
    <main className="page">
      <section className="hero"><h1>Reservations</h1></section>
      {error && <p className="error">{error}</p>}

      <section className="grid two">
        <div className="stack">
          <h2>Incoming requests for my tools</h2>
          {incoming.map((reservation) => reservationCard(reservation, "incoming"))}
        </div>
        <div className="stack">
          <h2>My outgoing reservations</h2>
          {outgoing.map((reservation) => reservationCard(reservation, "outgoing"))}
        </div>
      </section>

      {selected && (
        <section className="card">
          <h2>Reservation #{selected.id} thread</h2>
          <div className="message-list">
            {messages.map((message) => (
              <p key={message.id}><strong>{message.sender?.full_name ?? `User #${message.sender_id}`}:</strong> {message.body}</p>
            ))}
          </div>
          <form className="inline-form" onSubmit={sendMessage}>
            <input value={body} onChange={(event) => setBody(event.target.value)} placeholder="Write a message" required />
            <button type="submit">Send</button>
          </form>

          {selected.status === "RETURNED" && (
            <div className="stack compact">
              <h3>Leave a review</h3>
              <textarea value={reviewComment} onChange={(event) => setReviewComment(event.target.value)} />
              <button onClick={() => void submitReview()}>Submit 5-star review</button>
            </div>
          )}

          {(selected.status === "PICKED_UP" || selected.status === "RETURNED") && (
            <div className="stack compact">
              <h3>Report damage</h3>
              <textarea value={damageDescription} onChange={(event) => setDamageDescription(event.target.value)} />
              <button onClick={() => void submitDamageReport()}>Submit damage report</button>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
