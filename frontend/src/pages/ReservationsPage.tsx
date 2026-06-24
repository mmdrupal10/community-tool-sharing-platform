import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
    void loadReservations().catch((err) =>
      setError(err instanceof Error ? err.message : "Could not load reservations")
    );
  }, []);

  async function runAction(
    reservation: Reservation,
    action: "approve" | "deny" | "cancel" | "pickup" | "return"
  ) {
    setError("");

    try {
      await apiFetch<Reservation>(`/reservations/${reservation.id}/${action}`, {
        method: "POST"
      });

      await loadReservations();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    }
  }

  async function sendMessage(event: FormEvent) {
    event.preventDefault();

    if (!selected) return;

    await apiFetch<Message>(`/messages/${selected.id}`, {
      method: "POST",
      body: JSON.stringify({ body })
    });

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

        <p>
          <strong>Status:</strong> {reservation.status}
        </p>

        <p>
          {reservation.start_date} to {reservation.end_date}
        </p>

        <div className="actions wrap">
          {/* Tool owners can approve or deny new reservation requests. */}
          {mode === "incoming" && reservation.status === "REQUESTED" && (
            <button onClick={() => void runAction(reservation, "approve")}>
              Approve
            </button>
          )}

          {mode === "incoming" && reservation.status === "REQUESTED" && (
            <button onClick={() => void runAction(reservation, "deny")}>
              Deny
            </button>
          )}

          {/* Tool owners confirm the return after the borrower has picked up the tool. */}
          {mode === "incoming" && reservation.status === "PICKED_UP" && (
            <button onClick={() => void runAction(reservation, "return")}>
              Confirm returned
            </button>
          )}

          {/* Borrowers mark a reservation as picked up after it is approved. */}
          {mode === "outgoing" && reservation.status === "APPROVED" && (
            <button onClick={() => void runAction(reservation, "pickup")}>
              Mark picked up
            </button>
          )}

          {/* Cancellation is allowed only before pickup. */}
          {(reservation.status === "REQUESTED" || reservation.status === "APPROVED") && (
            <button onClick={() => void runAction(reservation, "cancel")}>
              Cancel
            </button>
          )}

          <button className="secondary" onClick={() => void loadMessages(reservation)}>
            Messages / Review
          </button>
        </div>
      </article>
    );
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <h1>Reservations</h1>
          <p>Manage incoming requests and outgoing reservations.</p>
        </div>

        {/* A new reservation starts by choosing an available tool first. */}
        <Link className="button" to="/tools">
          New Reservation
        </Link>
      </section>

      {error && <p className="error">{error}</p>}

      <section className="grid two">
        <div className="stack">
          <h2>Incoming requests for my tools</h2>

          {/* Tool owners will see borrower requests here. */}
          {incoming.length === 0 && (
            <p className="muted">No incoming requests yet.</p>
          )}

          {incoming.map((reservation) => reservationCard(reservation, "incoming"))}
        </div>

        <div className="stack">
          <h2>My outgoing reservations</h2>

          {/* Borrowers will see their reservation requests here. */}
          {outgoing.length === 0 && (
            <p className="muted">
              No outgoing reservations yet. Click New Reservation to request a tool.
            </p>
          )}

          {outgoing.map((reservation) => reservationCard(reservation, "outgoing"))}
        </div>
      </section>

      {selected && (
        <section className="card">
          <h2>Reservation #{selected.id} thread</h2>

          <div className="message-list">
            {messages.map((message) => (
              <p key={message.id}>
                <strong>{message.sender?.full_name ?? `User #${message.sender_id}`}:</strong>{" "}
                {message.body}
              </p>
            ))}
          </div>

          <form className="inline-form" onSubmit={sendMessage}>
            <input
              value={body}
              onChange={(event) => setBody(event.target.value)}
              placeholder="Write a message"
              required
            />

            <button type="submit">Send</button>
          </form>

          {/* Reviews are only allowed after the reservation is returned. */}
          {selected.status === "RETURNED" && (
            <div className="stack compact">
              <h3>Leave a review</h3>

              <textarea
                value={reviewComment}
                onChange={(event) => setReviewComment(event.target.value)}
              />

              <button onClick={() => void submitReview()}>
                Submit 5-star review
              </button>
            </div>
          )}

          {/* Damage reports are allowed after pickup or return. */}
          {(selected.status === "PICKED_UP" || selected.status === "RETURNED") && (
            <div className="stack compact">
              <h3>Report damage</h3>

              <textarea
                value={damageDescription}
                onChange={(event) => setDamageDescription(event.target.value)}
              />

              <button onClick={() => void submitDamageReport()}>
                Submit damage report
              </button>
            </div>
          )}
        </section>
      )}
    </main>
  );
}