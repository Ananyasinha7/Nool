"""Single source for frontend/src/i18n/{en,ta}.json so the key sets cannot drift.
Tamil strings are MACHINE-DRAFTED and need a native speaker's review before the demo (A-12).
Run: python scripts/gen_i18n.py"""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "frontend" / "src" / "i18n"

T: dict[str, tuple[str, str]] = {
    # common
    "common.today": ("Today", "இன்று"), "common.retry": ("Retry", "மீண்டும் முயற்சி"),
    "common.cancel": ("Cancel", "ரத்து"), "common.save": ("Save", "சேமி"), "common.saved": ("Saved", "சேமிக்கப்பட்டது"),
    "common.back": ("Back", "பின்"), "common.close": ("Close", "மூடு"), "common.next": ("Next", "அடுத்து"),
    "common.clearFilters": ("Clear filters", "வடிகட்டிகளை நீக்கு"), "common.all": ("All", "அனைத்தும்"),
    "common.signOut": ("Sign out", "வெளியேறு"), "common.demoDate": ("Demo date", "டெமோ தேதி"),
    "common.loading": ("Loading", "ஏற்றுகிறது"), "common.days": ("days", "நாட்கள்"), "common.day": ("day", "நாள்"),
    "common.onTime": ("on time", "சரியான நேரத்தில்"), "common.pcs": ("pcs", "எண்"),
    "common.language": ("Language", "மொழி"), "common.optional": ("optional", "விருப்பம்"),
    "common.none": ("None", "எதுவுமில்லை"), "common.details": ("Details", "விவரங்கள்"),
    "common.roleSupervisor": ("Supervisor", "மேற்பார்வையாளர்"), "common.roleMerchandiser": ("Merchandiser", "வணிகர்"),
    "common.roleBuyer": ("Buyer", "வாங்குபவர்"), "common.switchRole": ("Switch demo user", "டெமோ பயனர் மாற்று"),
    "common.role": ("Role", "பங்கு"), "common.unit": ("Unit", "பிரிவு"),
    "common.warningWaiting": ("Warning waiting", "எச்சரிக்கை காத்திருக்கிறது"),
    "common.previewBuyer": ("Buyer view", "வாங்குபவர் பார்வை"),
    "common.legendTick": ("Tick: Target by deadline", "குறி: காலக்கெடு இலக்கு"),
    "common.legendRate": ("Projection: At current run-rate", "கணிப்பு: தற்போதைய வேகம்"),
    "common.sortBy": ("Sort", "வரிசை"), "common.sortSeverity": ("Severity", "முன்னுரிமை"),
    "common.sortExFactory": ("Ex-factory date", "Ex-factory தேதி"), "common.sortQty": ("Quantity", "எண்ணிக்கை"),
    "common.sortPo": ("PO number", "PO எண்"),
    "common.shipImpactSafe": ("Ship date safe", "அனுப்பும் தேதி பாதுகாப்பானது"),
    "common.shipImpactSlip": ("Ship impact: +{n}d", "அனுப்பும் தாக்கம்: +{n}நா"),
    "common.todayEntries": ("Today's entries", "இன்றைய பதிவுகள்"),
    "common.queuedCount": ("{n} queued", "{n} வரிசையில் உள்ளது"),
    "common.sentCount": ("{n} sent", "{n} அனுப்பப்பட்டது"),
    # status
    "status.green": ("On track", "சரியாக உள்ளது"), "status.amber": ("Watch", "கவனம்"),
    "status.red": ("Late", "தாமதம்"), "status.grey": ("No recent update", "சமீபத்தில் புதுப்பிப்பு இல்லை"),
    # stage
    "stage.cutting": ("Cutting", "வெட்டுதல்"), "stage.printing": ("Printing", "அச்சிடுதல்"),
    "stage.stitching": ("Stitching", "தையல்"), "stage.washing": ("Washing", "சலவை"),
    "stage.finishing": ("Finishing", "ஃபினிஷிங்"), "stage.packing": ("Packing", "பேக்கிங்"),
    "stage.done": ("Complete", "முடிந்தது"),
    # auth
    "auth.signIn": ("Sign in", "உள்நுழை"), "auth.username": ("Username", "பயனர் பெயர்"),
    "auth.pin": ("Password or PIN", "கடவுச்சொல் / பின்"), "auth.demoLogins": ("Demo logins", "டெமோ உள்நுழைவுகள்"),
    "auth.signingIn": ("Signing in", "உள்நுழைகிறது"), "auth.tagline": ("Every order, on thread.", "ஒவ்வொரு ஆர்டரும் நூலில்."),
    "auth.useThis": ("Use", "பயன்படுத்து"),
    # errors (api code lower-cased)
    "err.validation": ("Please check the highlighted fields.", "குறிக்கப்பட்ட புலங்களைச் சரிபார்க்கவும்."),
    "err.unauthenticated": ("Please sign in.", "உள்நுழையவும்."),
    "err.forbidden": ("You do not have access to this.", "இதற்கு உங்களுக்கு அனுமதி இல்லை."),
    "err.not_found": ("Not found.", "கிடைக்கவில்லை."),
    "err.conflict": ("This conflicts with existing data.", "இது ஏற்கனவே உள்ள தரவுடன் முரண்படுகிறது."),
    "err.rate_limited": ("Too many attempts. Try again later.", "அதிக முயற்சிகள். பின்னர் முயற்சிக்கவும்."),
    "err.server": ("Something went wrong. Please try again.", "ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்."),
    "err.network": ("No connection.", "இணைய இணைப்பு இல்லை."),
    "err.qtyInvalid": ("Number looks wrong", "எண்ணிக்கை தவறாக உள்ளது"),
    "err.loadFailed": ("Could not load this. Retry.", "ஏற்ற முடியவில்லை. மீண்டும் முயற்சிக்கவும்."),
    "err.badLogin": ("Username or password is incorrect.", "பயனர் பெயர் அல்லது கடவுச்சொல் தவறானது."),
    # supervisor
    "sup.todayCount": ("Today's count", "இன்றைய எண்ணிக்கை"), "sup.needed": ("Needed today", "இன்று தேவை"),
    "sup.send": ("Send", "அனுப்பு"), "sup.photo": ("Photo", "படம்"), "sup.note": ("Note (optional)", "குறிப்பு (விருப்பம்)"),
    "sup.speak": ("Speak", "பேசு"), "sup.myOrders": ("My orders", "என் ஆர்டர்கள்"),
    "sup.hello": ("Hello", "வணக்கம்"), "sup.addCount": ("Add count", "எண்ணிக்கை சேர்"),
    "sup.noOrders": ("No orders for your unit today.", "இன்று உங்கள் பிரிவில் ஆர்டர்கள் இல்லை."),
    "sup.lastRefreshed": ("Last refreshed", "கடைசியாக புதுப்பிக்கப்பட்டது"),
    "sup.yesterday": ("Yesterday", "நேற்று"),
    "sup.moreThanRemaining": ("More than remaining. Send anyway?", "மீதமுள்ளதை விட அதிகம். அனுப்பவா?"),
    "sup.sendAnyway": ("Send anyway", "அனுப்பு"), "sup.removePhoto": ("Remove photo", "படத்தை நீக்கு"),
    "sup.recording": ("Recording", "பதிவு செய்கிறது"), "sup.stopRecording": ("Stop", "நிறுத்து"),
    "sup.holdToSpeak": ("Tap to start and stop", "தொடங்க / நிறுத்த தட்டவும்"),
    "sup.voiceAttached": ("Voice note added", "குரல் குறிப்பு சேர்க்கப்பட்டது"),
    "sup.installTitle": ("Add Nool to your home screen", "Nool-ஐ முகப்புத் திரையில் சேர்க்கவும்"),
    "sup.installBtn": ("Add", "சேர்"), "sup.installLater": ("Not now", "பின்னர்"),
    "sup.iosInstall": ("In Safari: Share, then Add to Home Screen.", "Safari-யில்: பகிர், பின்னர் முகப்புத் திரையில் சேர்."),
    "sup.signInAgain": ("Sign in again to send {n} updates.", "{n} புதுப்பிப்புகளை அனுப்ப மீண்டும் உள்நுழையவும்."),
    "sup.updateReady": ("New version ready.", "புதிய பதிப்பு தயார்."), "sup.reload": ("Reload", "மீண்டும் ஏற்று"),
    "sup.yourStage": ("Stage", "நிலை"), "sup.required": ("Required today", "இன்றைய இலக்கு"),
    "sup.unsentNote": ("Not sent yet", "இன்னும் அனுப்பவில்லை"),
    "sup.entryLogged": ("Entry registered", "எண்ணிக்கை பதிவானது"),
    "sup.todaysLog": ("Today's entries for this stage", "இந்த நிலையின் இன்றைய பதிவுகள்"),
    "sup.targetPill": ("Target: {needed}/day", "இலக்கு: {needed}/நாள்"),
    # queue and network
    "queue.queued": ("Queued", "வரிசையில் உள்ளது"), "queue.sending": ("Sending", "அனுப்புகிறது"),
    "queue.sent": ("Sent", "அனுப்பப்பட்டது"), "queue.failed": ("Failed — tap to retry", "தோல்வி — மீண்டும் முயற்சி"),
    "queue.allSent": ("All sent", "அனைத்தும் அனுப்பப்பட்டன"), "queue.sheetTitle": ("Updates", "புதுப்பிப்புகள்"),
    "queue.empty": ("Nothing waiting.", "எதுவும் காத்திருக்கவில்லை."), "queue.edit": ("Edit", "திருத்து"),
    "queue.failedChip": ("Failed", "தோல்வி"), "queue.photoItem": ("Photo", "படம்"), "queue.voiceItem": ("Voice", "குரல்"),
    "net.offline": ("No connection. Saved, will send when online.",
                    "இணைய இணைப்பு இல்லை. சேமிக்கப்படும், இணைப்பு வந்ததும் அனுப்பப்படும்."),
    "offline.title": ("You are offline", "நீங்கள் ஆஃப்லைனில் உள்ளீர்கள்"),
    "offline.body": ("This page is not saved on your phone yet. Your updates are safe in the queue.",
                     "இந்தப் பக்கம் இன்னும் தொலைபேசியில் சேமிக்கப்படவில்லை. உங்கள் புதுப்பிப்புகள் பாதுகாப்பாக உள்ளன."),
    # merchandiser shell and board
    "merch.board": ("Board", "பலகை"), "merch.warnings": ("Warnings", "எச்சரிக்கைகள்"),
    "merch.newOrder": ("New order", "புதிய ஆர்டர்"), "merch.outbox": ("Outbox", "வெளிச்செல்லும்"),
    "merch.orders": ("Orders", "ஆர்டர்கள்"), "merch.exportWeekly": ("Export weekly", "வாராந்திர ஏற்றுமதி"),
    "merch.buyer": ("Buyer", "வாங்குபவர்"), "merch.unit": ("Unit", "பிரிவு"), "merch.shipWeek": ("Ship week", "அனுப்பும் வாரம்"),
    "merch.status": ("Status", "நிலை"), "merch.searchPo": ("Search PO", "PO தேடு"), "merch.filters": ("Filters", "வடிகட்டிகள்"),
    "merch.colOrder": ("Order", "ஆர்டர்"), "merch.colStage": ("Stage", "நிலை"), "merch.colProgress": ("Progress", "முன்னேற்றம்"),
    "merch.colShip": ("Ship", "அனுப்பல்"), "merch.colProjection": ("Projection", "கணிப்பு"),
    "merch.empty": ("No orders yet. Create the first one.", "ஆர்டர்கள் இல்லை. முதல் ஆர்டரை உருவாக்கவும்."),
    "merch.emptyFiltered": ("No orders match.", "பொருந்தும் ஆர்டர்கள் இல்லை."),
    "merch.flaggedEarly": ("flagged {n} days early", "{n} நாட்கள் முன்பே கண்டறியப்பட்டது"),
    "merch.flaggedBefore": ("flagged {n} days before ship", "அனுப்புவதற்கு {n} நாட்கள் முன் கண்டறியப்பட்டது"),
    "merch.slipDays": ("+{n} days", "+{n} நாட்கள்"), "merch.slipDay": ("+1 day", "+1 நாள்"),
    "merch.lowConfidence": ("Planned rate (no updates yet)", "திட்ட வேகம் (புதுப்பிப்பு இல்லை)"),
    "merch.filtersBtn": ("Filters ({n})", "வடிகட்டிகள் ({n})"), "merch.apply": ("Apply", "பயன்படுத்து"),
    "merch.needMaking": ("Need {need}/d · making {making}/d", "தேவை {need}/நா · செய்வது {making}/நா"),
    "merch.stageOverdue": ("Stage deadline passed", "நிலை காலக்கெடு முடிந்தது"),
    "merch.viewOrder": ("Open order", "ஆர்டரைத் திற"), "merch.userMenu": ("Account", "கணக்கு"),
    # order detail
    "order.timeline": ("Timeline", "காலவரிசை"), "order.output": ("Daily output", "தினசரி உற்பத்தி"),
    "order.issues": ("Issues", "சிக்கல்கள்"), "order.history": ("Date history", "தேதி வரலாறு"),
    "order.maths": ("Need {need}/day · Making {making}/day · {days} working days left",
                    "தேவை {need}/நாள் · செய்வது {making}/நாள் · {days} வேலை நாட்கள் மீதம்"),
    "order.overdue": ("Stage deadline has passed · {rem} pieces left", "நிலை காலக்கெடு முடிந்தது · {rem} எண் மீதம்"),
    "order.projected": ("Projected finish {date} · {slip} working days late", "கணிக்கப்பட்ட முடிவு {date} · {slip} வேலை நாட்கள் தாமதம்"),
    "order.projectedOk": ("Projected finish {date} · on time", "கணிக்கப்பட்ட முடிவு {date} · சரியான நேரத்தில்"),
    "order.shipImpact": ("Projected ship {date} · {slip} working days after ex-factory",
                         "கணிக்கப்பட்ட அனுப்பல் {date} · ex-factory-க்கு {slip} வேலை நாட்கள் பின்"),
    "order.recovery": ("To close the gap: +{n} pieces a day", "இடைவெளியை மூட: தினமும் +{n} எண்"),
    "order.noUpdates": ("No updates yet. Planned rate shown.", "புதுப்பிப்புகள் இல்லை. திட்ட வேகம் காட்டப்படுகிறது."),
    "order.changeDate": ("Change date", "தேதியை மாற்று"), "order.exFactory": ("Ex-factory", "Ex-factory"),
    "order.newDate": ("New date", "புதிய தேதி"), "order.reasonLabel": ("Reason", "காரணம்"),
    "order.reasonText": ("Details", "விவரங்கள்"),
    "order.reason.BUYER_REQUEST": ("Buyer request", "வாங்குபவர் கோரிக்கை"),
    "order.reason.MATERIAL_DELAY": ("Material delay", "பொருள் தாமதம்"), "order.reason.CAPACITY": ("Capacity", "திறன்"),
    "order.reason.OTHER": ("Other", "மற்றவை"),
    "order.planned": ("Planned", "திட்டம்"), "order.actual": ("Actual", "உண்மை"), "order.tick": ("Mark done", "முடிந்தது எனக் குறி"),
    "order.untick": ("Undo", "திரும்பப்பெறு"),
    "order.noChanges": ("No date changes", "தேதி மாற்றங்கள் இல்லை"), "order.noIssues": ("No issues reported.", "சிக்கல்கள் இல்லை."),
    "order.pendingWarning": ("Pending delay warning awaiting review", "மதிப்பாய்வுக்காக காத்திருக்கும் தாமத எச்சரிக்கை"),
    "order.reviewWarning": ("Review warning", "எச்சரிக்கையை மதிப்பாய்வு செய்"),
    "order.previewBuyerView": ("Preview buyer view", "வாங்குபவர் பார்வையை முன்னோட்டம் செய்"),
    "order.colDate": ("Date", "தேதி"), "order.colQty": ("Quantity", "எண்ணிக்கை"), "order.colBy": ("Entered by", "பதிவு செய்தவர்"),
    "order.original": ("Original note", "அசல் குறிப்பு"), "order.translation": ("English translation", "ஆங்கில மொழிபெயர்ப்பு"),
    "order.category": ("Category", "வகை"), "order.from": ("From", "இருந்து"), "order.to": ("To", "வரை"),
    "order.by": ("By", "செய்தவர்"), "order.dateSaved": ("Date changed", "தேதி மாற்றப்பட்டது"),
    "order.tickSaved": ("Saved", "சேமிக்கப்பட்டது"), "order.sharePhoto": ("Share with buyer", "வாங்குபவருடன் பகிர்"),
    "order.noLogs": ("No daily numbers yet.", "தினசரி எண்கள் இல்லை."), "order.photoShared": ("Shared", "பகிரப்பட்டது"),
    "order.photoInternal": ("Internal", "உள்ளக"),
    "cat.MACHINE_BREAKDOWN": ("Machine breakdown", "இயந்திரம் பழுது"), "cat.POWER_CUT": ("Power cut", "மின்வெட்டு"),
    "cat.ABSENTEEISM": ("Staff absence", "ஆட்கள் வரவில்லை"), "cat.MATERIAL_SHORTAGE": ("Material shortage", "பொருள் பற்றாக்குறை"),
    "cat.QUALITY_REWORK": ("Quality rework", "தரம் / மறுவேலை"), "cat.SUBCONTRACTOR_DELAY": ("Subcontractor delay", "வெளி நிறுவன தாமதம்"),
    "cat.APPROVAL_PENDING": ("Approval pending", "அனுமதி நிலுவை"), "cat.OTHER": ("Other", "மற்றவை"),
    "cat.NEEDS_REVIEW": ("Needs review", "சரிபார்க்க வேண்டும்"),
    # setup
    "setup.title": ("New order", "புதிய ஆர்டர்"), "setup.step1": ("Order", "ஆர்டர்"), "setup.step2": ("Quantities", "எண்ணிக்கைகள்"),
    "setup.step3": ("Dates and plan", "தேதிகள் மற்றும் திட்டம்"), "setup.step4": ("Review", "மதிப்பாய்வு"),
    "setup.po": ("PO number", "PO எண்"), "setup.style": ("Style", "ஸ்டைல்"), "setup.colour": ("Colour", "நிறம்"),
    "setup.pickBuyer": ("Choose a buyer", "வாங்குபவரைத் தேர்வு செய்"), "setup.pickUnit": ("Choose a unit", "பிரிவைத் தேர்வு செய்"),
    "setup.hasPrint": ("Printed style", "அச்சிடப்பட்ட ஸ்டைல்"), "setup.printUnit": ("Printing unit", "அச்சிடும் பிரிவு"),
    "setup.size": ("Size", "அளவு"), "setup.total": ("Total", "மொத்தம்"), "setup.addSize": ("Add size", "அளவு சேர்"),
    "setup.exFactory": ("Ex-factory date", "Ex-factory தேதி"), "setup.template": ("TNA template", "TNA வார்ப்புரு"),
    "setup.milestones": ("Milestones", "மைல்கற்கள்"), "setup.create": ("Create order", "ஆர்டரை உருவாக்கு"),
    "setup.created": ("Order created", "ஆர்டர் உருவாக்கப்பட்டது"), "setup.loadSample": ("Load a sample", "மாதிரியை ஏற்று"),
    "setup.edit": ("Edit", "திருத்து"), "setup.required": ("Required", "தேவை"), "setup.mustSum": ("Lines must add up to the total.", "வரிகள் மொத்தத்துடன் பொருந்த வேண்டும்."),
    "setup.qtyInvalid": ("Enter whole numbers above zero.", "பூஜ்ஜியத்துக்கு மேல் முழு எண்களை உள்ளிடவும்."),
    "setup.dateFuture": ("Pick a date after today.", "இன்றைக்குப் பிறகான தேதியைத் தேர்வு செய்."),
    "setup.noLines": ("Add at least one quantity.", "குறைந்தது ஒரு எண்ணிக்கையைச் சேர்."),
    "setup.dupPo": ("This PO already exists.", "இந்த PO ஏற்கனவே உள்ளது."),
    # warnings
    "warn.inbox": ("Warnings", "எச்சரிக்கைகள்"), "warn.confirm": ("Confirm and send to buyer", "உறுதிசெய்து வாங்குபவருக்கு அனுப்பு"),
    "warn.dismiss": ("Dismiss", "நிராகரி"), "warn.needsReview": ("Needs review", "சரிபார்க்க வேண்டும்"),
    "warn.confHigh": ("High", "அதிகம்"), "warn.confUnsure": ("Unsure", "உறுதியில்லை"),
    "warn.buyerPreview": ("What the buyer will see", "வாங்குபவர் பார்ப்பது"),
    "warn.empty": ("No warnings waiting. You are up to date.", "காத்திருக்கும் எச்சரிக்கைகள் இல்லை."),
    "warn.sentMock": ("Sent to {buyer} (mock)", "{buyer}-க்கு அனுப்பப்பட்டது (மாதிரி)"), "warn.viewOutbox": ("View outbox", "வெளிச்செல்லும் பார்"),
    "warn.dismissed": ("Dismissed", "நிராகரிக்கப்பட்டது"), "warn.pickCategory": ("Pick a category to continue", "தொடர வகையைத் தேர்வு செய்"),
    "warn.noNote": ("No note was written.", "குறிப்பு எழுதப்படவில்லை."), "warn.maths": ("The maths at the time", "அப்போதைய கணக்கு"),
    "warn.aiSource": ("Suggested by AI", "AI பரிந்துரை"), "warn.ruleSource": ("Keyword match", "சொல் பொருத்தம்"),
    "warn.humanSource": ("Set by you", "நீங்கள் அமைத்தது"), "outbox.title": ("Outbox", "வெளிச்செல்லும்"),
    "outbox.note": ("Messages are simulated in this demo.", "இந்த டெமோவில் செய்திகள் மாதிரியாக மட்டுமே."),
    "outbox.to": ("To", "பெறுநர்"), "outbox.subject": ("Subject", "பொருள்"), "outbox.time": ("Time", "நேரம்"),
    "outbox.empty": ("No messages yet.", "செய்திகள் இல்லை."),
    # buyer
    "buyer.header": ("Order status", "ஆர்டர் நிலை"), "buyer.from": ("Status updates from Company A", "Company A-யிலிருந்து நிலை புதுப்பிப்புகள்"),
    "buyer.delayNotice": ("Delay notice", "தாமத அறிவிப்பு"), "buyer.noPhotos": ("No photos shared yet.", "பகிரப்பட்ட படங்கள் இல்லை."),
    "buyer.invalid": ("This link is no longer active. Please contact your merchandiser.", "இந்த இணைப்பு செயலில் இல்லை. உங்கள் merchandiser-ஐத் தொடர்பு கொள்ளவும்."),
    "buyer.download": ("Download this week's status (Excel)", "இந்த வார நிலையைப் பதிவிறக்கு (Excel)"),
    "buyer.timeline": ("Milestones", "மைல்கற்கள்"), "buyer.photos": ("Photos", "படங்கள்"), "buyer.history": ("Date changes", "தேதி மாற்றங்கள்"),
    "buyer.progress": ("Progress", "முன்னேற்றம்"), "buyer.noChanges": ("No date changes", "தேதி மாற்றங்கள் இல்லை"),
    "buyer.opening": ("Opening your orders", "உங்கள் ஆர்டர்களைத் திறக்கிறது"), "buyer.noOrders": ("No orders yet.", "ஆர்டர்கள் இல்லை."),
    "buyer.qty": ("pcs", "எண்"), "buyer.shipDate": ("Ex-factory", "Ex-factory"),
    "export.week": ("Week", "வாரம்"), "export.done": ("Download started", "பதிவிறக்கம் தொடங்கியது"),
}


CORE_NS = {"common", "stage", "auth", "err", "sup", "queue", "net", "offline"}


def nest(flat: dict[str, str]) -> dict:
    root: dict = {}
    for key, value in flat.items():
        node = root
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = value
    return root


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    # core = what the supervisor/login route needs (loaded eagerly, keeps the floor bundle small, NFR-1);
    # app = merchandiser and buyer strings, loaded together with those route chunks.
    for i, lang in enumerate(("en", "ta")):
        for part, pick in (("core", lambda k: k.split(".")[0] in CORE_NS), ("app", lambda k: k.split(".")[0] not in CORE_NS)):
            data = nest({k: v[i] for k, v in T.items() if pick(k)})
            (OUT / f"{lang}.{part}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for old in ("en.json", "ta.json"):
        (OUT / old).unlink(missing_ok=True)
    print(len(T), "keys")
