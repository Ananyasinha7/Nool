import { useCallback, useEffect, useRef, useState } from "react";

const memCache = new Map<string, unknown>();

/** Loads data and keeps the last good copy visible while reloading (stale-while-revalidate). */
export function useAsync<T>(fn: () => Promise<T>, deps: unknown[], cacheKey?: string) {
  const fnKey = fn.toString().replace(/\s+/g, " ").slice(0, 80);
  const key = cacheKey ?? (deps.length > 0 ? `${fnKey}:${JSON.stringify(deps)}` : undefined);
  const cached = key ? (memCache.get(key) as T | undefined) : undefined;
  const [data, setData] = useState<T | undefined>(cached);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(cached === undefined);
  const [tick, setTick] = useState(0);
  const fnRef = useRef(fn);
  fnRef.current = fn;
  useEffect(() => {
    let alive = true;
    if (cached === undefined) setLoading(true);
    fnRef.current()
      .then((d) => {
        if (key) memCache.set(key, d);
        if (alive) { setData(d); setError(null); setLoading(false); }
      })
      .catch((e: unknown) => { if (alive) { setError(e); setLoading(false); } });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick]);
  const reload = useCallback(() => setTick((x) => x + 1), []);
  return { data, error, loading, reload, setData };
}
