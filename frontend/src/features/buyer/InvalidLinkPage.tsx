import "../../i18n/app";
import { useT } from "../../i18n/provider";

/** Calm, with no detail leaked: an unknown and a revoked link look identical. */
export default function InvalidLinkPage() {
  const t = useT();
  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center px-6 text-center">
      <p role="alert" className="text-heading">{t("buyer.invalid")}</p>
    </main>
  );
}
