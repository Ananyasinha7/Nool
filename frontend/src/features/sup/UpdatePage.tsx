import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import config from "../../../../contract/config.json";
import { api } from "../../api/client";
import type { SupOrderCard } from "../../api/types";
import { ConfirmMoreSheet } from "../../components/sup/ConfirmMoreSheet";
import { MicButton } from "../../components/sup/MicButton";
import { NoteField } from "../../components/sup/NoteField";
import { PhotoButton } from "../../components/sup/PhotoButton";
import { QuantityStepper } from "../../components/sup/QuantityStepper";
import { SendBar } from "../../components/sup/SendBar";
import { SupHeader } from "../../components/sup/SupHeader";
import { EmptyState, SkeletonRows } from "../../components/ui";
import { useI18n } from "../../i18n/provider";
import { db } from "../../lib/offline/db";
import { loadCards, readCachedCards } from "../../lib/offline/ordersCache";
import { submitEntry } from "../../lib/offline/useSubmit";
import { fmtNum } from "../../lib/format";
import { setToday } from "../../lib/today";
import { usePageTitle } from "../../lib/usePageTitle";

export default function UpdatePage() {
  const { orderId = "", stage = "" } = useParams();
  const { t } = useI18n();
  const nav = useNavigate();
  const [all, setAll] = useState<SupOrderCard[] | null>(null);
  const card = useMemo(() => all?.find((c) => c.orderId === orderId && c.stageKey === stage) ?? null, [all, orderId, stage]);
  usePageTitle(card?.poNo ? `${card.poNo} (${t(`stage.${stage.toLowerCase()}`)})` : t("sup.addCount"));
  const [qty, setQty] = useState("");
  const [note, setNote] = useState("");
  const [photo, setPhoto] = useState<Blob | null>(null);
  const [audio, setAudio] = useState<Blob | null>(null);
  const [hint, setHint] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirm, setConfirm] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    void api.healthz().then((h) => setToday(h.today)).catch(() => undefined);
    void readCachedCards().then((c) => setAll(c?.cards ?? null)).then(() => loadCards().then((r) => r && setAll(r.cards)));
  }, []);
  const siblings = all?.filter((c) => c.orderId === orderId) ?? [];

  // The last number sent from this phone for this order and stage is the grey hint (not pre-filled).
  useEffect(() => {
    void db.outbox.orderBy("createdAt").reverse().filter((i) => i.log?.orderId === orderId && i.log?.stageKey === stage).first().then((i) => setHint(i?.log?.qty ?? null));
  }, [orderId, stage]);

  const n = qty === "" ? null : Number(qty);
  const remaining = useMemo(() => (card ? Math.max(0, card.qty - card.done + (card.todayQty ?? 0)) : 0), [card]);

  async function save() {
    if (!card || n === null) return;
    await submitEntry({ card, qty: n, note, photo: photo ?? undefined, audio: audio ?? undefined }); // durable locally, then back at once
    navigator.vibrate?.(10);
    setDone(true);
    setTimeout(() => nav("/s", { replace: true }), 400); // the check shows for 400 ms: well inside 600 ms
  }
  function trySend() {
    if (!card || n === null || !Number.isInteger(n) || n < 0) { setError(t("err.qtyInvalid")); return; }
    const cumulative = card.done - (card.todayQty ?? 0) + n;
    if (cumulative > config.qtyCap * card.qty) { setError(t("err.qtyInvalid")); return; } // server enforces too (BR-09)
    setError(null);
    if (n > remaining) { setConfirm(true); return; }
    void save();
  }

  if (all === null) return <><SupHeader back="/s" /><div className="mx-auto w-full max-w-2xl p-4 md:p-6"><SkeletonRows n={2} /></div></>;
  if (!card) return <><SupHeader back="/s" /><div className="mx-auto w-full max-w-2xl p-4 md:p-6"><EmptyState text={t("sup.noOrders")} actionLabel={t("common.back")} onAction={() => nav("/s")} /></div></>;

  return (
    <>
      <SupHeader back="/s" title={card.poNo} />
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-5 px-4 py-4 md:px-6 md:py-6">
        <p className="text-ink-2">{card.style} · {t(`stage.${card.stageKey.toLowerCase()}`)}</p>
        {siblings.length > 1 && (
          <div role="group" aria-label={t("sup.yourStage")} className="flex overflow-hidden rounded border border-field">
            {siblings.map((s) => (
              <button key={s.stageKey} type="button" aria-pressed={s.stageKey === stage} onClick={() => nav(`/s/update/${orderId}/${s.stageKey}`, { replace: true })}
                      className={`min-h-[48px] flex-1 ${s.stageKey === stage ? "bg-ink text-paper" : "bg-surface"}`}>{t(`stage.${s.stageKey.toLowerCase()}`)}</button>
            ))}
          </div>
        )}
        <div className="flex items-center justify-between rounded-lg border border-line bg-paper px-4 py-2.5">
          <span className="text-ink-2 font-medium">{t("sup.needed")}</span>
          <span className="rounded bg-ink px-3 py-1 text-base font-semibold text-paper">{fmtNum(card.neededToday)} {t("common.pcs")}</span>
        </div>
        <QuantityStepper value={qty} onChange={(v) => { setQty(v); setError(null); }} hint={hint} error={error} />
        {card.todayQty !== null && card.todayQty > 0 && (
          <p className="text-center text-sm text-ink-2">{t("sup.todaysLog")}: <b className="text-ink">{fmtNum(card.todayQty)}</b> {t("common.pcs")}</p>
        )}
        <div className="flex flex-wrap items-center gap-4">
          <PhotoButton blob={photo} onChange={setPhoto} />
          <MicButton blob={audio} onChange={setAudio} />
        </div>
        <NoteField value={note} onChange={setNote} />
      </main>
      <SendBar onSend={trySend} disabled={n === null} done={done} />
      <ConfirmMoreSheet open={confirm} remaining={remaining} onCancel={() => setConfirm(false)} onConfirm={() => { setConfirm(false); void save(); }} />
    </>
  );
}
