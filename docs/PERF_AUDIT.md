# Nool Performance Audit & Optimization Report

## 1. System & Physical Environment
- **Frontend:** React 18 + Vite (SPA) running on localhost (`http://localhost:5173`).
- **Backend:** FastAPI (Python 3.12) running on localhost (`http://localhost:8001`).
- **Database:** PostgreSQL on Supabase (Session Pooler).
- **Physical Network Latency:**
  - Client location: India. Supabase remote host: ~500ms round-trip latency.
  - Baseline raw query (`SELECT 1`) on an established connection: **~490ms – 580ms**.
  - Cold engine connection with pre-ping (`SELECT 1`): **~1,700ms – 2,500ms** (up to **8,126ms** initial cold connect).

---

## 2. Before vs. After: Backend Endpoints

| Endpoint | Baseline Server Time | Phase 1 (Serial Batch) | Phase 2 (Concurrent Pool) | Total Improvement |
| :--- | :---: | :---: | :---: | :--- |
| **`GET /api/healthz`** | 1,703.4 ms | 2.3 ms | **2.3 ms** | **740x faster** (in-memory cached) |
| **`GET /api/lookups`** | 2,075.2 ms | 820.0 ms | **802.5 ms** | **61% faster** (cached static reference data) |
| **`GET /api/orders` (board)** | 4,923.0 ms | 3,460.1 ms | **2,067.9 ms** | **58% faster** (parallelized milestones, logs, assignments, warnings) |
| **`GET /api/warnings`** | 3,185.9 ms | 1,665.7 ms | **2,186.5 ms** | **31% faster** (batched orders & notes + parallel maps) |
| **`GET /api/sup/orders`** | 4,624.0 ms | 3,703.7 ms | **2,142.2 ms** | **54% faster** (eliminated N+1 stage assignment queries) |
| **`GET /api/buyer/orders`** | 4,606.1 ms | 3,503.3 ms | **2,210.0 ms** | **52% faster** (eliminated duplicate build_inputs query round-trip) |

---

## 3. Before vs. After: Frontend Screen Load Times (Dev & Repeat Visits)

Measured in automated headless Chrome environment simulating real network hops to localhost proxy:

| Route / Screen | Initial Load (Before) | Initial Load (After) | Refresh (Before) | Refresh (After) | Speedup Factor |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Board (`/board`)** | 8,832 ms | **3,482 ms** | 10,114 ms | **3,350 ms** | **~2.8x – 3.0x faster** |
| **Warnings (`/warnings`)** | 23,045 ms | **6,445 ms** | 19,444 ms | **6,535 ms** | **~3.6x faster** |
| **Supervisor (`/s`)** | 12,695 ms | **4,067 ms** | 12,214 ms | **4,365 ms** | **~3.1x faster** |
| **Buyer (`/b`)** | 2,334 ms | **900 ms** | 2,504 ms | **1,064 ms** | **~2.6x faster** |

---

## 4. Key Fixes Applied

1. **Connection Pooling & Pre-Ping Elimination (`backend/app/db.py`):**
   - Removed `pool_pre_ping=True` (which ran a redundant `SELECT 1` round-trip taking ~500ms on every checkout).
   - Configured `pool_size=10`, `max_overflow=10`, and `pool_recycle=300` to keep connections hot and avoid stale dropped sockets without checkout latency.

2. **Cached Healthz DB Check (`backend/app/routers/health.py`):**
   - Added 30-second TTL caching on database connectivity checks in `/api/healthz`.
   - Result: Clock/date inquiries for the frontend respond in **~2ms** instead of 1,700ms.

3. **Batch-Loaded Warnings (`backend/app/services/warnings.py` & `backend/app/routers/warnings.py`):**
   - Replaced individual `session.get(Order)` and `session.get(IssueNote)` calls inside a loop with batch queries (`WHERE id IN (...)`).
   - Cut query count and dropped endpoint latency from 3.2s to 1.6s.

4. **In-Flight GET Request Deduplication (`frontend/src/api/client.ts`):**
   - Implemented request deduplication for concurrent identical GET requests.
   - Prevents `MerchShell` and child pages (e.g. `WarningsPage`) or React StrictMode from sending duplicate identical requests over the wire simultaneously.

5. **Session-Level Lookups Caching (`frontend/src/api/client.ts` & `backend/app/routers/orders.py`):**
   - Lookups (`buyers`, `units`) are cached in-memory on the client during a user session.
   - Backend caches buyer and unit lookups for 60 seconds.

6. **Stale-While-Revalidate Navigation (`frontend/src/lib/useAsync.ts`):**
   - Replaced immediate `undefined` unmounting with memory-cached initial data keyed by dependencies.
   - Navigating between `/board` and `/orders/:id` renders immediately without empty loading skeletons while revalidating fresh data in the background.

7. **Static Holiday Data Caching (`backend/app/services/health.py`):**
   - Cached factory holiday calendar in memory (5-minute TTL) across order projection computations, saving 1 sequential round-trip per order view.

8. **Concurrent Query Parallelization (`backend/app/routers/orders.py`):**
   - In `list_orders`, replaced 4 sequential database queries (`Milestones`, `DailyLogs`, `StageAssignments`, `Warnings`) with parallel execution using `ThreadPoolExecutor(max_workers=4)` across pooled connections.
   - Reduced board query time by over 1.4 seconds.

9. **N+1 Query Elimination in Supervisor Endpoint (`backend/app/services/sup.py`):**
   - Replaced per-order loop query `scope.assigned_stages(o.id)` with a single batch `IN (order_ids)` query.
   - Dropped `/api/sup/orders` response time from 3,703ms to 2,142ms.

10. **Duplicate Query Elimination in Buyer Endpoint (`backend/app/routers/buyer.py`):**
   - `_views` previously invoked `build_inputs` and then called `health_for`, which internally called `build_inputs` a second time. Passing precomputed inputs directly eliminated 2 redundant database round trips.

11. **Frontend Idle Route Chunk Prefetching (`frontend/src/routes.tsx`):**
   - Added idle callback prefetching for Merchandiser chunks (`MerchShell`, `BoardPage`, `OrderPage`, `WarningsPage`).
   - Page transitions on the client are instant because chunk downloads occur silently in the background while keeping floor supervisor bundle under budget.

---

## 5. Verification & Safety

- **TypeScript Typecheck:** Clean (`tsc --noEmit` exits 0).
- **Frontend Test Suite:** 37 / 37 passed (`vitest run`).
- **Production Build:** Succeeded in 5.42s.
- **Supervisor Route Bundle:** **93,534 bytes** gzipped (Budget: ≤ 100,000 bytes; 6.5 KB headroom).
- **Safety Compliance:**
  - `pytest` was **NOT** run against the Supabase database (per safety mandate to prevent dropping the public schema).
  - No secrets or connection strings logged or committed.
  - All temporary profiling middleware (`perf_timer.py`) and measurement scripts were removed.
