import { useState } from "react";
import { BottomSheet, Button, EmptyState, ErrorState, LangToggle, ProgressBar, Select, Skeleton, StatusBadge, TextInput, Timeline, Wordmark, useToast } from "../components/ui";
import type { Health } from "../api/types";

const H: Health[] = ["GREEN", "AMBER", "RED", "GREY"];

/** Dev-only (/dev/styleguide): every component in every state, for the design QA pass. */
export default function Styleguide() {
  const [open, setOpen] = useState(false);
  const [sel, setSel] = useState("");
  const toast = useToast();
  return (
    <main className="mx-auto flex max-w-page flex-col gap-8 p-6">
      <Wordmark tamil />
      <section className="flex flex-wrap gap-3">{H.map((h) => <StatusBadge key={h} health={h} />)}</section>
      <section className="flex flex-wrap gap-3">
        <Button>Primary</Button><Button variant="secondary">Secondary</Button><Button variant="ghost">Ghost</Button><Button variant="danger">Danger</Button><Button disabled>Disabled</Button><Button loading>Loading</Button><Button sup>Send (56px)</Button>
      </section>
      <section className="flex max-w-md flex-col gap-3">{H.map((h, i) => <ProgressBar key={h} done={20 + i * 20} qty={100} health={h} tickAt={70} />)}</section>
      <section className="grid max-w-xl gap-4 md:grid-cols-2">
        <TextInput label="Label" helper="Helper text" /><TextInput label="With error" error="Required" defaultValue="x" />
        <Select label="Select" value={sel} onChange={setSel} placeholder="Choose" options={[{ value: "a", label: "A" }, { value: "b", label: "B" }]} />
      </section>
      <section className="flex gap-3"><LangToggle /><Button variant="secondary" onClick={() => setOpen(true)}>Bottom sheet</Button><Button variant="secondary" onClick={() => toast.show("Saved", { label: "Undo", onClick: () => undefined })}>Toast</Button></section>
      <section className="max-w-md"><Timeline today="2026-11-03" items={[{ name: "Sample approved", plannedDate: "2026-10-12", actualDate: "2026-10-12" }, { name: "Fabric in-house", plannedDate: "2026-10-20", actualDate: null, manual: true }, { name: "Stitching complete", plannedDate: "2026-11-13", actualDate: null }]} onTick={() => undefined} /></section>
      <section className="grid gap-4 md:grid-cols-3"><Skeleton className="h-16" /><EmptyState text="Empty state" actionLabel="Action" onAction={() => undefined} /><ErrorState onRetry={() => undefined} detail="Detail" /></section>
      <BottomSheet open={open} onClose={() => setOpen(false)} title="Sheet"><p>Body</p></BottomSheet>
    </main>
  );
}
