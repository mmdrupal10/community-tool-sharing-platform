import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function ProtectedRoute({ children }: { children: ReactElement }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <main className="page"><p>Loading...</p></main>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
