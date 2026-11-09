"""Pre-classified Tamil notes, warnings and date changes for the demo (Doc3 section 13).

Tamil text here is machine-drafted and needs a native speaker's review (A-12)."""
from __future__ import annotations

# po -> (original, lang, translation, category, confidence)
NOTES: list[tuple[str, str, str, str, str, float]] = [
    ("B-PO-88240", "2 தையல் மெசின் பழுது", "ta", "2 sewing machines are broken", "MACHINE_BREAKDOWN", 0.93),
    ("B-PO-88301", "இன்று மின்சாரம் 3 மணி நேரம் இல்லை", "ta", "No electricity for 3 hours today",
     "POWER_CUT", 0.95),
    ("B-PO-88213", "machine problem, 2 hours stop", "en", "Machine problem, 2 hours stoppage",
     "MACHINE_BREAKDOWN", 0.9),
    ("B-PO-88213", "நீல நிற துணி வரவில்லை", "ta", "The navy fabric has not arrived", "MATERIAL_SHORTAGE", 0.9),
    ("C-PO-0491", "15 ஆட்கள் வரவில்லை", "ta", "15 workers did not come in", "ABSENTEEISM", 0.92),
    ("B-PO-88317", "வெட்டு அளவில் தவறு, மறுவேலை", "ta", "Error in cutting size, rework needed",
     "QUALITY_REWORK", 0.88),
]

# Draft warnings (merchandiser must still confirm): po -> index into NOTES
DRAFT_WARNINGS = {"B-PO-88240": 0, "B-PO-88301": 1}
# One confirmed warning so the buyer view has content
CONFIRMED_WARNING = ("B-PO-88213", 2)

# po -> [(from, to, reason_code, reason_text, days before today, actor)]
DATE_CHANGES = {
    "B-PO-88213": [("2026-11-11", "2026-11-16", "MATERIAL_DELAY", "Trims arrived late", 14),
                   ("2026-11-16", "2026-11-20", "BUYER_REQUEST", "Buyer moved the delivery slot", 6)],
}
