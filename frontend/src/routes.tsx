import { Suspense, lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { RequireRole, homeFor } from "./components/shell/RequireRole";
import { Skeleton } from "./components/ui";
import SupHomePage from "./features/sup/SupHomePage";
import SupLayout from "./features/sup/SupLayout";
import UpdatePage from "./features/sup/UpdatePage";
import { useAuth } from "./lib/auth";

const LoginPage = lazy(() => import("./features/auth/LoginPage"));
const OfflinePage = lazy(() => import("./pages/OfflinePage"));

// The supervisor route group is eager (small, must open offline); merchandiser and buyer code is split
// into their own chunks so the floor bundle stays under 100 KB gzipped (NFR-1).
const MerchShell = lazy(() => import("./components/shell/MerchShell").then((m) => ({ default: m.MerchShell })));
const BoardPage = lazy(() => import("./features/merch/board/BoardPage"));
const OrderPage = lazy(() => import("./features/merch/order/OrderPage"));
const SetupPage = lazy(() => import("./features/merch/setup/SetupPage"));
const WarningsPage = lazy(() => import("./features/merch/warnings/WarningsPage"));
const OutboxPage = lazy(() => import("./features/merch/outbox/OutboxPage"));
const BuyerEntry = lazy(() => import("./features/buyer/BuyerEntry"));
const BuyerListPage = lazy(() => import("./features/buyer/BuyerListPage"));
const BuyerOrderPage = lazy(() => import("./features/buyer/BuyerOrderPage"));
const Styleguide = import.meta.env.DEV ? lazy(() => import("./pages/Styleguide")) : null;

// Prefetch merchandiser chunks when browser is idle so navigation is instant
if (typeof window !== "undefined") {
  const scheduleIdle = window.requestIdleCallback || ((cb: () => void) => setTimeout(cb, 1200));
  scheduleIdle(() => {
    import("./components/shell/MerchShell");
    import("./features/merch/board/BoardPage");
    import("./features/merch/order/OrderPage");
    import("./features/merch/warnings/WarningsPage");
  });
}

function Root() {
  const { me, loading } = useAuth();
  if (loading && !me) return <div className="p-6"><Skeleton className="h-10 w-48" /></div>;
  return <Navigate to={me ? homeFor(me.role) : "/login"} replace />;
}

export function AppRoutes() {
  return (
    <Suspense fallback={<div className="p-6"><Skeleton className="h-10 w-48" /></div>}>
      <Routes>
        <Route path="/" element={<Root />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/offline" element={<OfflinePage />} />
        <Route element={<RequireRole roles={["SUPERVISOR"]}><SupLayout /></RequireRole>}>
          <Route path="/s" element={<SupHomePage />} />
          <Route path="/s/update/:orderId/:stage" element={<UpdatePage />} />
        </Route>
        <Route element={<RequireRole roles={["MERCHANDISER"]}><MerchShell /></RequireRole>}>
          <Route path="/board" element={<BoardPage />} />
          <Route path="/orders/new" element={<SetupPage />} />
          <Route path="/orders/:id" element={<OrderPage />} />
          <Route path="/warnings" element={<WarningsPage />} />
          <Route path="/outbox" element={<OutboxPage />} />
        </Route>
        <Route path="/b/:token" element={<BuyerEntry />} />
        <Route path="/b" element={<RequireRole roles={["BUYER"]}><BuyerListPage /></RequireRole>} />
        <Route path="/b/orders/:id" element={<RequireRole roles={["BUYER"]}><BuyerOrderPage /></RequireRole>} />
        {Styleguide && <Route path="/dev/styleguide" element={<Styleguide />} />}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
