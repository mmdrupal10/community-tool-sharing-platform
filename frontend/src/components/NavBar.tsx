import { Link, NavLink } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function NavBar() {
  const { user, logout } = useAuth();

  return (
    <header className="topbar">
      <Link className="brand" to="/">ToolShare</Link>
      <nav>
        {user ? (
          <>
            <NavLink to="/dashboard">Dashboard</NavLink>
            <NavLink to="/tools">Browse</NavLink>
            <NavLink to="/my-tools">My Tools</NavLink>
            <NavLink to="/reservations">Reservations</NavLink>
            {user.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
            <button className="link-button" onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <NavLink to="/login">Login</NavLink>
            <NavLink to="/register">Register</NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
