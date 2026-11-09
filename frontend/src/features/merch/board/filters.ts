import type { Health } from "../../../api/types";

/** Board filters live in the URL so a view can be bookmarked (Doc2 S-2). */
export type SortKey = "severity" | "exFactory" | "qty" | "po";
export interface BoardFilters { buyerId?: string; unitId?: string; week?: string; status?: Health; q?: string; sort?: SortKey }

const STATUSES: Health[] = ["GREEN", "AMBER", "RED", "GREY"];

export function parseFilters(params: URLSearchParams): BoardFilters {
  const status = params.get("status") as Health | null;
  return {
    buyerId: params.get("buyer") || undefined,
    unitId: params.get("unit") || undefined,
    week: params.get("week") || undefined,
    status: status && STATUSES.includes(status) ? status : undefined,
    q: params.get("q") || undefined,
    sort: (params.get("sort") as SortKey | null) || undefined,
  };
}

export function toParams(f: BoardFilters): URLSearchParams {
  const p = new URLSearchParams();
  if (f.buyerId) p.set("buyer", f.buyerId);
  if (f.unitId) p.set("unit", f.unitId);
  if (f.week) p.set("week", f.week);
  if (f.status) p.set("status", f.status);
  if (f.q) p.set("q", f.q);
  if (f.sort) p.set("sort", f.sort);
  return p;
}

export function activeCount(f: BoardFilters): number {
  return [f.buyerId, f.unitId, f.week, f.status, f.q, f.sort].filter(Boolean).length;
}

/** Query for the API: the board asks the server for everything the filters select except status,
 * so the summary strip counts stay stable while one status is selected. */
export function apiQuery(f: BoardFilters) {
  return { buyerId: f.buyerId, unitId: f.unitId, shipWeek: f.week, q: f.q };
}
