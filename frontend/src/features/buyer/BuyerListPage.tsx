import { api, errorKey } from "../../api/client";
import { BuyerHeader } from "../../components/buyer/BuyerHeader";
import { BuyerOrderRow } from "../../components/buyer/BuyerOrderRow";
import { EmptyState, ErrorState, SkeletonRows } from "../../components/ui";
import { useI18n } from "../../i18n/provider";
import { useAuth } from "../../lib/auth";
import { useAsync } from "../../lib/useAsync";
import { usePageTitle } from "../../lib/usePageTitle";
import { ApiException } from "../../api/client";
import InvalidLinkPage from "./InvalidLinkPage";

export default function BuyerListPage() {
  const { t } = useI18n();
  usePageTitle(t("buyer.header"));
  const { me } = useAuth();
  const orders = useAsync(() => api.buyerOrders(), []);
  if (orders.error instanceof ApiException && orders.error.status === 401) return <InvalidLinkPage />; // revoked while open
  return (
    <>
      <BuyerHeader company={me?.buyerName ?? ""} />
      <main className="mx-auto flex max-w-page flex-col gap-6 px-4 py-6 md:px-6">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-title font-semibold">{t("buyer.header")}</h1>
            <p className="text-[13px] text-ink-3 sm:hidden">{me?.buyerName ? `${me.buyerName} · ` : ""}{t("buyer.from")}</p>
          </div>
          <a href={api.exportUrl()} download className="inline-flex min-h-[36px] sm:min-h-[44px] items-center text-ink-2 underline hover:text-ink text-[13px] sm:text-sm">{t("buyer.download")} ↓</a>
        </div>
        {orders.loading && !orders.data ? <SkeletonRows n={4} />
          : orders.error ? <ErrorState message={t(errorKey(orders.error))} onRetry={orders.reload} />
          : !orders.data?.length ? <EmptyState text={t("buyer.noOrders")} />
          : <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">{orders.data.map((o) => <BuyerOrderRow key={o.id} o={o} />)}</div>}
      </main>
    </>
  );
}
