import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../lib/auth";
import { Skeleton } from "../ui";
import type { ReactNode } from "react";

export function homeFor(role: string): string {
  return role === "SUPERVISOR" ? "/s" : role === "BUYER" ? "/b" : "/board";
}

export function RequireRole({ roles, children }: { roles: string[]; children: ReactNode }) {
  const { me, loading } = useAuth();
  const loc = useLocation();
  if (!me && loading) return <div className="p-6"><Skeleton className="h-10 w-48" /></div>;
  if (!me) return <Navigate to={`/login?returnTo=${encodeURIComponent(loc.pathname + loc.search)}`} replace />;
  if (!roles.includes(me.role)) return <Navigate to={homeFor(me.role)} replace />;
  return <>{children}</>;
}
