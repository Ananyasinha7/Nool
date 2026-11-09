import { useState } from "react";
import { useT } from "../../../i18n/provider";
import type { Health, Lookups } from "../../../api/types";
import { BottomSheet, Button, Select, TextInput } from "../../../components/ui";
import { activeCount, type BoardFilters, type SortKey } from "./filters";

interface Props { filters: BoardFilters; lookups?: Lookups; onChange: (f: BoardFilters) => void; onClear: () => void }

export function FilterBar({ filters, lookups, onChange, onClear }: Props) {
  const t = useT();
  const [open, setOpen] = useState(false);
  const set = (patch: Partial<BoardFilters>) => onChange({ ...filters, ...patch });
  const all = t("common.all");
  const statusOpts = (["RED", "AMBER", "GREEN", "GREY"] as Health[]).map((h) => ({ value: h, label: t(`status.${h.toLowerCase()}`) }));
  const sortOpts: { value: SortKey; label: string }[] = [
    { value: "severity", label: t("common.sortSeverity") },
    { value: "exFactory", label: t("common.sortExFactory") },
    { value: "qty", label: t("common.sortQty") },
    { value: "po", label: t("common.sortPo") },
  ];

  const fields = (
    <>
      <Select label={t("merch.buyer")} value={filters.buyerId ?? ""} onChange={(v) => set({ buyerId: v || undefined })} placeholder={all}
              options={(lookups?.buyers ?? []).map((b) => ({ value: b.id, label: b.name }))} />
      <Select label={t("merch.unit")} value={filters.unitId ?? ""} onChange={(v) => set({ unitId: v || undefined })} placeholder={all}
              options={(lookups?.units ?? []).map((u) => ({ value: u.id, label: u.name }))} />
      <Select label={t("merch.shipWeek")} value={filters.week ?? ""} onChange={(v) => set({ week: v || undefined })} placeholder={all}
              options={(lookups?.shipWeeks ?? []).map((w) => ({ value: w, label: w }))} />
      <Select label={t("merch.status")} value={filters.status ?? ""} onChange={(v) => set({ status: (v || undefined) as Health | undefined })} placeholder={all} options={statusOpts} />
    </>
  );
  const n = activeCount(filters);
  return (
    <>
      <div className="hidden items-end gap-3 md:grid md:grid-cols-[repeat(4,1fr)_auto_1.2fr_auto]">
        {fields}
        <Select label={t("common.sortBy")} value={filters.sort ?? ""} onChange={(v) => set({ sort: (v || undefined) as SortKey | undefined })} placeholder={t("common.sortSeverity")} options={sortOpts} />
        <TextInput label={t("merch.searchPo")} type="search" value={filters.q ?? ""} onChange={(e) => set({ q: e.target.value || undefined })} />
        {n > 0 && <Button variant="ghost" onClick={onClear}>{t("common.clearFilters")}</Button>}
      </div>
      <div className="flex items-end gap-2 md:hidden">
        <div className="flex-1"><TextInput label={t("merch.searchPo")} type="search" value={filters.q ?? ""} onChange={(e) => set({ q: e.target.value || undefined })} /></div>
        <Button variant="secondary" onClick={() => setOpen(true)}>{t("merch.filtersBtn", { n })}</Button>
      </div>
      <BottomSheet open={open} onClose={() => setOpen(false)} title={t("merch.filters")}>
        <div className="flex flex-col gap-4">
          {fields}
          <Select label={t("common.sortBy")} value={filters.sort ?? ""} onChange={(v) => set({ sort: (v || undefined) as SortKey | undefined })} placeholder={t("common.sortSeverity")} options={sortOpts} />
          <div className="flex gap-2">
            <Button variant="ghost" className="flex-1" onClick={() => { onClear(); setOpen(false); }}>{t("common.clearFilters")}</Button>
            <Button className="flex-1" onClick={() => setOpen(false)}>{t("merch.apply")}</Button>
          </div>
        </div>
      </BottomSheet>
    </>
  );
}
