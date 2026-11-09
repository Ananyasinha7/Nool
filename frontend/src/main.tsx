import { Component, StrictMode, type ErrorInfo, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import { api } from "./api/client";
import { ToastProvider } from "./components/ui";
import { I18nProvider } from "./i18n/provider";
import { AuthProvider } from "./lib/auth";
import { setToday } from "./lib/today";
import { AppRoutes } from "./routes";

class Boundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(e: Error, info: ErrorInfo) { console.error(e, info.componentStack); }
  render() {
    return this.state.failed
      ? <div role="alert" className="p-8 text-center"><p>Something went wrong.</p><button className="mt-4 underline" onClick={() => location.reload()}>Reload</button></div>
      : this.props.children;
  }
}

// The server's date (demo clock aware) is cached for offline use; failure is harmless.
void api.healthz().then((h) => setToday(h.today)).catch(() => undefined);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Boundary>
      <I18nProvider>
        <AuthProvider>
          <ToastProvider>
            <BrowserRouter><AppRoutes /></BrowserRouter>
          </ToastProvider>
        </AuthProvider>
      </I18nProvider>
    </Boundary>
  </StrictMode>,
);
