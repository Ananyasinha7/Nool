"""Deterministic Tamil keyword fallback (BR-07). Works with no network and no key.

Starter list from Doc3 section 11; a native speaker must review it (A-12).
Rule results are always source=RULE with confidence <= 0.6, so they always need review (TD-7)."""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

KEYWORDS: dict[str, tuple[str, ...]] = {
    "POWER_CUT": ("மின்சாரம்", "கரண்ட்", "மின்வெட்டு", "power"),
    "MACHINE_BREAKDOWN": ("மெசின்", "இயந்திரம்", "பழுது", "ரிப்பேர்", "machine"),
    "ABSENTEEISM": ("ஆட்கள் வரவில்லை", "ஆட்கள் இல்லை", "absent"),
    "MATERIAL_SHORTAGE": ("துணி", "நூல்", "டிரிம்ஸ்", "பட்டன்", "ஜிப்", "fabric"),
    "QUALITY_REWORK": ("மறுவேலை", "ரீவொர்க்", "கறை", "ஓட்டை", "தவறு", "rework"),
    "APPROVAL_PENDING": ("அனுமதி", "அப்ரூவல்", "சாம்பிள்", "approval"),
}
_SUB_PARTY = ("பிரிண்டிங்", "வாஷிங்")
_SUB_DELAY = ("தாமதம்", "வரவில்லை")
MAX_RULE_CONFIDENCE = 0.6


@dataclass(frozen=True)
class RuleResult:
    category: str
    confidence: float
    evidence: str


def normalise(text: str) -> str:
    return unicodedata.normalize("NFC", text).strip().lower()


def classify_rules(text: str) -> RuleResult:
    t = normalise(text)
    hits: dict[str, list[str]] = {}
    for cat, words in KEYWORDS.items():
        found = [w for w in words if w in t]
        if found:
            hits[cat] = found
    party = [w for w in _SUB_PARTY if w in t]
    delay = [w for w in _SUB_DELAY if w in t]
    if party and delay:
        hits["SUBCONTRACTOR_DELAY"] = party + delay  # needs both parts together
    if not hits:
        return RuleResult("NEEDS_REVIEW", 0.0, "")
    best = max(len(v) for v in hits.values())
    top = [c for c, v in hits.items() if len(v) == best]
    if len(top) > 1:  # tie: do not guess
        return RuleResult("NEEDS_REVIEW", 0.3, ", ".join(hits[top[0]]))
    cat = top[0]
    return RuleResult(cat, min(MAX_RULE_CONFIDENCE, 0.3 + 0.15 * best), ", ".join(hits[cat]))
