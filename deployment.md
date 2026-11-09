# Nool: deployment and run guide

Every order, on thread. Python 3.12 + FastAPI backend, React + Vite PWA frontend, Postgres (Neon).

> **Status of this guide.** The code was built and tested in Claude's sandbox against a real Postgres 16.
> Deployment to Vercel/Neon/Groq, a real phone, GitHub Actions and Playwright were **not** exercised there
> (no credentials or browser download). Those steps below are written from the docs and are marked
> **UNVERIFIED** until you have run them. See `docs/BUILD_REPORT.md`.

## 1. Local run (Windows, PowerShell)

Prerequisites: Python 3.12, Node LTS, Git, VS Code. Check: `py -3.12 --version` and `node --version`.

```powershell
cd $HOME\Documents\nool
copy .env.example .env          # then edit .env LOCALLY (never commit it, never paste it anywhere)
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1    # if blocked: Set-ExecutionPolicy -Scope Process Bypass  (or use Git Bash: source .venv/Scripts/activate)
pip install -r backend/requirements-dev.txt
alembic -c backend/alembic.ini upgrade head
python -m backend.seed
uvicorn backend.app.main:app --reload --port 8000
```

Second PowerShell window:

```powershell
cd $HOME\Documents\nool
npm --prefix frontend install
npm --prefix frontend run dev        # http://localhost:5173 (proxies /api to port 8000)
```

Activate the venv in every new terminal. Run backend commands from the repo root.

### Database for local development

Create a free Neon project, then put the **pooled** string in `DATABASE_URL` and the **direct** string in
`DIRECT_URL`. Neon shows `postgresql://...`; change the prefix to **`postgresql+psycopg://`**.
Use a Neon *dev branch* for development and tests, never your production branch.

The app starts without Groq: leave `AI_MODE=mock` and `GROQ_API_KEY` empty and the classifier answers from the
golden set or the deterministic Tamil keyword rules.

## 2. Environment variables (names only)

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL`, `DIRECT_URL` | Neon pooled and direct strings (`postgresql+psycopg://`) |
| `JWT_SECRET` | Cookie signing. **32+ random characters; the app refuses to start with `ENV=prod` otherwise** |
| `GROQ_API_KEY` | Groq access (optional: mock/rules work without it) |
| `GROQ_CLASSIFY_MODEL`, `GROQ_CLASSIFY_FALLBACKS`, `GROQ_STT_MODEL` | Model names. **Check the Groq console: names change** |
| `AI_MODE` | `mock` or `live` |
| `DEMO_TODAY` | `2026-11-03`: keeps seeded colours stable. Leave empty for a real rollout |
| `DEMO_LOGINS_VISIBLE` | Reserved for the backend flag; the sign-in screen's flag is `VITE_DEMO_LOGINS` |
| `APP_URL` | Absolute URL used in buyer links |
| `ENV` | `dev` or `prod` (API docs, `Secure` cookies, NullPool) |
| `VITE_API_BASE`, `VITE_USE_FIXTURES`, `VITE_DEMO_LOGINS` | Frontend, build time. `VITE_API_BASE` defaults to `/api` |

Generate a secret: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

## 3. Demo logins (synthetic, demo only)

| Username | Secret | Role |
| --- | --- | --- |
| `priya.merch` | `Nool@Demo2026` | Merchandiser (English) |
| `murugan.u1` | `246810` | Supervisor, Unit 1 (Tamil) |
| `selvi.u2` | `246810` | Supervisor, Unit 2 |
| `kumar.print` | `246810` | Supervisor, Print House |
| `anbu.u3` | `246810` | Supervisor, Unit 3 |

Buyer magic links (demo tokens, **public**): `/b/demo-b-0001` (Company B), `/b/demo-c-0001` (Company C),
`/b/demo-d-0001` (Company D). Delete or revoke them and change every demo credential before any real use.
Five wrong attempts lock an account for 10 minutes.

The seeded board (demo date Tue 3 Nov 2026) shows 2 Late, 3 Watch, 7 On track, 1 No recent update. The three
client samples: B-PO-88213 Watch, B-PO-88240 Late, C-PO-0488 On track.

## 4. Seed, reseed

```powershell
python -m backend.seed      # idempotent: skips orders that already exist
```

To reset a development database completely: drop and recreate the schema in the Neon console (dev branch only),
then run `alembic ... upgrade head` and the seed again.

## 5. Tests and checks

```powershell
ruff check backend scripts
$env:TEST_DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST/DBNAME"   # a THROWAWAY database
pytest -q
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
```

`pytest` **drops and rebuilds the `public` schema of `TEST_DATABASE_URL`**. Without that variable, database-backed
tests are skipped (the projection, rules and workday tests still run). Never point it at production.

After any API change: `python scripts/export_openapi.py` then `npm --prefix frontend run gen:types`, and commit
both generated files. CI fails if they are stale. After editing translations: `python scripts/gen_i18n.py`.

Browser end-to-end (UNVERIFIED): `cd frontend; npx playwright install chromium; npm run e2e` (needs a seeded
dev database in `DATABASE_URL`).

## 6. Deploy (UNVERIFIED: run gate G0 first)

### Option 1 (preferred): Vercel for both

1. Push the repo to GitHub (public). Confirm `git log` and `git ls-files` contain no `.env`.
2. Import it into Vercel. `vercel.json` already sets the build (`cd frontend && npm ci && npm run build`),
   output (`frontend/dist`), the `/api/*` rewrite to the Python function `api/index.py`, and security headers.
3. Set the environment variables from section 2 (with `ENV=prod`, a real `JWT_SECRET`, `APP_URL` = your URL).
4. **Gate G0:** open `https://YOUR-URL/api/healthz`. Success = `{"ok":true,"db":true,"today":"..."}` and the SPA
   loads from the same URL. Pick the Vercel function region closest to your Neon region.
5. Seed production once, from your machine: set `DATABASE_URL` to the production string, run
   `alembic -c backend/alembic.ini upgrade head` then `python -m backend.seed`.
6. Test on a real Android phone over HTTPS (install, airplane-mode submit, reconnect).

### Option 2 (fallback): API on Render, SPA on Vercel

Run the API on Render's free web service (`uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`) and add a
Vercel rewrite from `/api/:path*` to the Render URL so the browser still sees one origin (no CORS, simple
cookies). Render's free tier sleeps when idle and wakes slowly: use a free uptime pinger on `/api/healthz`.

## 7. Known limits (read before demoing)

- **Not yet seen in a real browser or on a phone.** The offline engine is proven by automated tests against a
  fake server (airplane mode, reconnect, one effective row, 401 pause, failed items kept). The UI, install
  prompt, camera, microphone and Lighthouse targets have not been exercised.
- **Tamil strings and golden-set labels are machine-drafted** and need a native speaker (A-12).
- **Groq was never called.** Models, accuracy and latency tables for Groq are not run; only the rules table exists.
- The mock outbox is the only "sending": no email or WhatsApp leaves the system.
- Notes sent to Groq must be synthetic in the demo. A real rollout needs a data-handling decision.
- Postgres row-level security for buyer tables is a stated next step, not built (isolation is enforced in one
  scoped data layer plus explicit response models, with negative tests).
- Dark mode, buyer Tamil, and Workbox Background Sync are not built (cut or deferred; see `docs/BUILD_REPORT.md`).
- The `Select` is the native element everywhere (no custom desktop popover).
- A voice note is one note per log entry; a retried audio upload is ignored once the log has a note.
