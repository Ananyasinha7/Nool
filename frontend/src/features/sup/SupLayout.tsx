import { Outlet } from "react-router-dom";
import { OfflineBanner } from "../../components/sup/OfflineBanner";
import { UpdateToast } from "../../components/sup/UpdateToast";

/** Supervisor shell: responsive on mobile, tablet, and desktop. Safe-area padded. */
export default function SupLayout() {
  return (
    <div className="mx-auto flex min-h-screen w-full flex-col bg-paper">
      <OfflineBanner />
      <Outlet />
      <UpdateToast />
    </div>
  );
}
