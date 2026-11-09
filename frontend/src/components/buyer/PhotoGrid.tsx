import { useState } from "react";
import { useI18n } from "../../i18n/provider";
import { fmtDate } from "../../lib/format";
import type { BuyerOrderDetail } from "../../api/types";
import { BottomSheet } from "../ui";

/** 3 columns on mobile, lightbox on tap (Doc2 C-17). Shared photos only, newest first. */
export function PhotoGrid({ photos, po }: { photos: BuyerOrderDetail["photos"]; po: string }) {
  const { t, lang } = useI18n();
  const [open, setOpen] = useState<number | null>(null);
  if (photos.length === 0) return <p className="text-ink-2">{t("buyer.noPhotos")}</p>;
  const cur = open !== null ? photos[open] : null;
  return (
    <>
      <ul className="grid grid-cols-3 gap-2 md:grid-cols-6">
        {photos.map((p, i) => (
          <li key={p.id}>
            <button type="button" className="block w-full" onClick={() => setOpen(i)}>
              <img src={p.url} alt={`${po}, ${fmtDate(p.takenOn, lang)}`} loading="lazy" className="aspect-square w-full rounded object-cover" />
              <span className="text-[12px] text-ink-3">{fmtDate(p.takenOn, lang)}</span>
            </button>
          </li>
        ))}
      </ul>
      <BottomSheet open={cur !== null} onClose={() => setOpen(null)} title={cur ? `${po} · ${fmtDate(cur.takenOn, lang)}` : ""}>
        {cur && <img src={cur.url} alt={`${po}, ${fmtDate(cur.takenOn, lang)}`} className="w-full rounded" />}
      </BottomSheet>
    </>
  );
}
