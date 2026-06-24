import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import type { Tool } from "../types";

const emptyTool = {
  name: "Circular Saw",
  description: "Corded circular saw for small projects.",
  category: "Power Tools",
  condition: "Good",
  photo_url: "",
  lending_rules: "Return clean and dry."
};

export default function MyToolsPage() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [form, setForm] = useState(emptyTool);
  const [error, setError] = useState("");

  async function loadTools() {
    setTools(await apiFetch<Tool[]>("/tools/mine"));
  }

  useEffect(() => {
    void loadTools().catch((err) => setError(err instanceof Error ? err.message : "Could not load tools"));
  }, []);

  async function createTool(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await apiFetch<Tool>("/tools", {
        method: "POST",
        body: JSON.stringify({ ...form, photo_url: form.photo_url || null })
      });
      setForm(emptyTool);
      await loadTools();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create tool");
    }
  }

  async function toggleVisibility(tool: Tool) {
    await apiFetch<Tool>(`/tools/${tool.id}/${tool.is_active ? "hide" : "show"}`, { method: "PATCH" });
    await loadTools();
  }

  async function deleteTool(tool: Tool) {
    await apiFetch<void>(`/tools/${tool.id}`, { method: "DELETE" });
    await loadTools();
  }

  return (
    <main className="page">
      <section className="hero"><h1>My tool listings</h1></section>
      {error && <p className="error">{error}</p>}

      <section className="grid two">
        <form className="card stack" onSubmit={createTool}>
          <h2>Add a tool</h2>
          <label>Name<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required /></label>
          <label>Description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} required /></label>
          <label>Category<input value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} required /></label>
          <label>Condition<input value={form.condition} onChange={(event) => setForm({ ...form, condition: event.target.value })} required /></label>
          <label>Photo URL<input value={form.photo_url} onChange={(event) => setForm({ ...form, photo_url: event.target.value })} /></label>
          <label>Lending rules<textarea value={form.lending_rules} onChange={(event) => setForm({ ...form, lending_rules: event.target.value })} /></label>
          <button type="submit">Create listing</button>
        </form>

        <div className="stack">
          {tools.map((tool) => (
            <article className="card" key={tool.id}>
              <h2>{tool.name}</h2>
              <p>{tool.description}</p>
              <p><strong>Status:</strong> {tool.is_active ? "Visible" : "Hidden"}</p>
              <div className="actions">
                <button onClick={() => void toggleVisibility(tool)}>{tool.is_active ? "Hide" : "Show"}</button>
                <button className="danger" onClick={() => void deleteTool(tool)}>Delete</button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
