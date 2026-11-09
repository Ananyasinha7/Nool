import "../../i18n/app";
import { useEffect, useState } from "react";
import { Navigate, useParams } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../lib/auth";
import { useT } from "../../i18n/provider";
import { Skeleton } from "../../components/ui";
import InvalidLinkPage from "./InvalidLinkPage";

/** /b/:token -> POST /api/buyer/session -> /b. The token is replaced in history so it is not left in the URL bar. */
export default function BuyerEntry() {
  const { token = "" } = useParams();
  const { refresh } = useAuth();
  const t = useT();
  const [state, setState] = useState<"loading" | "ok" | "invalid">("loading");
  useEffect(() => {
    let alive = true;
    api.buyerSession(token).then(() => refresh()).then(() => alive && setState("ok")).catch(() => alive && setState("invalid"));
    return () => { alive = false; };
  }, [token, refresh]);
  if (state === "ok") return <Navigate to="/b" replace />;
  if (state === "invalid") return <InvalidLinkPage />;
  return <div className="p-6" role="status" aria-label={t("buyer.opening")}><Skeleton className="h-10 w-64" /></div>;
}
