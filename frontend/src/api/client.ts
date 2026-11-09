// The single place that talks to the backend. Typed from src/api/types.gen.ts.
import { fixtures } from "./fixtures";
import type {
  ApiErrorBody, BuyerOrderDetail, BuyerOrderView, EditableCategory, ExFactoryChangeIn, ExFactoryChangeOut,
  Health, LogInput, LogRow, Lookups, MeOut, NoteView, OrderCreate, OrderDetail, OrderSummary, OutboxOut,
  TnaTemplateOut, WarningView, SupOrderCard, MilestoneOut,
} from "./types";

const BASE: string = import.meta.env.VITE_API_BASE ?? "/api";
const USE_FIXTURES = import.meta.env.VITE_USE_FIXTURES === "true";

export class ApiException extends Error {
  constructor(public status: number, public code: ApiErrorBody["code"] | "NETWORK", message: string,
              public fields?: Record<string, string> | null) {
    super(message);
  }
}

async function parseError(res: Response): Promise<ApiException> {
  try {
    const body = (await res.json()) as { error?: ApiErrorBody };
    if (body.error) return new ApiException(res.status, body.error.code, body.error.message, body.error.fields);
  } catch { /* not JSON */ }
  return new ApiException(res.status, res.status >= 500 ? "SERVER" : "VALIDATION", res.statusText);
}

const inFlight = new Map<string, Promise<unknown>>();
let lookupsCache: Promise<Lookups> | null = null;

async function call<T>(method: string, path: string, body?: unknown): Promise<T> {
  if (USE_FIXTURES && method === "GET") {
    const key = path.split("?")[0];
    if (key in fixtures) return fixtures[key] as T;
  }
  if (method === "GET") {
    const existing = inFlight.get(path);
    if (existing) return existing as Promise<T>;
  }
  const p = (async () => {
    try {
      const res = await fetch(`${BASE}${path}`, {
        method, credentials: "same-origin",
        headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
      if (!res.ok) throw await parseError(res);
      return (res.status === 204 ? undefined : await res.json()) as T;
    } catch (err) {
      if (err instanceof ApiException) throw err;
      throw new ApiException(0, "NETWORK", "No connection.");
    } finally {
      if (method === "GET") inFlight.delete(path);
    }
  })();
  if (method === "GET") inFlight.set(path, p);
  return p;
}

const qs = (p: Record<string, string | undefined>) => {
  const u = new URLSearchParams();
  for (const [k, v] of Object.entries(p)) if (v) u.set(k, v);
  const s = u.toString();
  return s ? `?${s}` : "";
};

export interface OrderFilters { buyerId?: string; unitId?: string; shipWeek?: string; status?: Health; q?: string }

export const api = {
  healthz: () => call<{ ok: boolean; db: boolean; today: string }>("GET", "/healthz"),
  // auth
  login: (username: string, password: string) => call<MeOut>("POST", "/auth/login", { username, password }),
  logout: () => call<{ ok: boolean }>("POST", "/auth/logout"),
  me: () => call<MeOut>("GET", "/me"),
  setLang: (lang: "en" | "ta") => call<MeOut>("PATCH", "/me", { lang }),
  // merchandiser
  orders: (f: OrderFilters = {}) => call<OrderSummary[]>("GET", `/orders${qs({ ...f })}`),
  order: (id: string) => call<OrderDetail>("GET", `/orders/${id}`),
  createOrder: (b: OrderCreate) => call<{ id: string }>("POST", "/orders", b),
  orderLogs: (id: string, days = 10) => call<LogRow[]>("GET", `/orders/${id}/logs?days=${days}`),
  orderChanges: (id: string) => call<ExFactoryChangeOut[]>("GET", `/orders/${id}/changes`),
  changeExFactory: (id: string, b: ExFactoryChangeIn) => call<OrderDetail>("PATCH", `/orders/${id}/ex-factory`, b),
  tickMilestone: (id: string, actualDate: string | null) => call<MilestoneOut>("PATCH", `/milestones/${id}`, { actualDate }),
  templates: () => call<TnaTemplateOut[]>("GET", "/tna-templates"),
  lookups: () => {
    if (!lookupsCache) lookupsCache = call<Lookups>("GET", "/lookups");
    return lookupsCache;
  },
  notes: (orderId: string) => call<NoteView[]>("GET", `/notes?orderId=${orderId}`),
  setNoteCategory: (id: string, category: EditableCategory) => call<NoteView>("PATCH", `/notes/${id}`, { category }),
  warnings: () => call<WarningView[]>("GET", "/warnings"),
  confirmWarning: (id: string, category: EditableCategory) => call<WarningView>("POST", `/warnings/${id}/confirm`, { category }),
  dismissWarning: (id: string) => call<WarningView>("POST", `/warnings/${id}/dismiss`),
  sharephoto: (id: string, shareWithBuyer: boolean) => call<{ id: string }>("PATCH", `/photos/${id}`, { shareWithBuyer }),
  outbox: () => call<OutboxOut[]>("GET", "/outbox"),
  exportUrl: (week?: string, buyerId?: string) => `${BASE}/export/weekly${qs({ week, buyerId })}`,
  // supervisor
  supOrders: () => call<SupOrderCard[]>("GET", "/sup/orders"),
  // buyer
  buyerSession: (token: string) => call<{ ok: boolean }>("POST", "/buyer/session", { token }),
  buyerOrders: () => call<BuyerOrderView[]>("GET", "/buyer/orders"),
  buyerOrder: (id: string) => call<BuyerOrderDetail>("GET", `/buyer/orders/${id}`),
};

// Raw calls for the offline sync engine: it needs the status code, not an exception.
export const raw = {
  postLog: (b: LogInput) => fetch(`${BASE}/logs`, { method: "POST", credentials: "same-origin",
    headers: { "Content-Type": "application/json" }, body: JSON.stringify(b) }),
  postPhoto: (logId: string, photoId: string, blob: Blob) => {
    const f = new FormData();
    f.set("photoId", photoId);
    f.set("file", blob, "photo.jpg");
    return fetch(`${BASE}/logs/${logId}/photo`, { method: "POST", credentials: "same-origin", body: f });
  },
  postAudio: (logId: string, blob: Blob) => {
    const f = new FormData();
    f.set("file", blob, "note.webm");
    return fetch(`${BASE}/logs/${logId}/audio`, { method: "POST", credentials: "same-origin", body: f });
  },
};

/** Maps an error to the key of a translated message: the API sends a code, the UI shows err.<code>. */
export function errorKey(e: unknown): string {
  if (e instanceof ApiException) return e.code === "NETWORK" ? "err.network" : `err.${e.code.toLowerCase()}`;
  return "err.server";
}
