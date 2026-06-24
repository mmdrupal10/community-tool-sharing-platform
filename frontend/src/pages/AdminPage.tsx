import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { Tool, User } from "../types";

type Report = Record<string, unknown>;

export default function AdminPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<Report | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [error, setError] = useState("");

  async function loadAdminData() {
    const [reportData, userRows, toolRows] = await Promise.all([
      apiFetch<Report>("/admin/reports"),
      apiFetch<User[]>("/admin/users"),
      apiFetch<Tool[]>("/admin/tools")
    ]);
    setReports(reportData);
    setUsers(userRows);
    setTools(toolRows);
  }

  useEffect(() => {
    if (user?.role === "admin") {
      void loadAdminData().catch((err) => setError(err instanceof Error ? err.message : "Could not load admin data"));
    }
  }, [user]);

  async function toggleSuspension(member: User) {
    await apiFetch<User>(`/admin/users/${member.id}/suspend`, {
      method: "PATCH",
      body: JSON.stringify({ is_suspended: !member.is_suspended })
    });
    await loadAdminData();
  }

  async function toggleToolActivation(tool: Tool) {
    await apiFetch<Tool>(`/admin/tools/${tool.id}/activation`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: !tool.is_active })
    });
    await loadAdminData();
  }

  if (user?.role !== "admin") {
    return <main className="page"><p className="error">Admin role required.</p></main>;
  }

  return (
    <main className="page">
      <section className="hero"><h1>Admin</h1><p>Manage users, hide listings, and view basic reports.</p></section>
      {error && <p className="error">{error}</p>}

      <section className="card">
        <h2>Reports</h2>
        <pre className="report">{JSON.stringify(reports, null, 2)}</pre>
      </section>

      <section className="grid two">
        <div className="stack">
          <h2>Users</h2>
          {users.map((member) => (
            <article className="card" key={member.id}>
              <h3>{member.full_name}</h3>
              <p>{member.email} - {member.role}</p>
              <p>{member.is_suspended ? "Suspended" : "Active"}</p>
              {member.id !== user.id && <button onClick={() => void toggleSuspension(member)}>{member.is_suspended ? "Unsuspend" : "Suspend"}</button>}
            </article>
          ))}
        </div>
        <div className="stack">
          <h2>Tools</h2>
          {tools.map((tool) => (
            <article className="card" key={tool.id}>
              <h3>{tool.name}</h3>
              <p>{tool.category} - {tool.is_active ? "Visible" : "Hidden"}</p>
              <button onClick={() => void toggleToolActivation(tool)}>{tool.is_active ? "Hide" : "Show"}</button>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
