# Reference Screen Captures (`docs/screens/`)

This directory contains the visual verification screenshots for the Nool application across desktop (1280px) and mobile floor phones (360px).

---

### Newly Appended Views (Latest Redesign & Floor Optimizations)

| File | Screen View | Viewport | Key Features Captured |
|---|---|---|---|
| `01_merchandiser_board_desktop.png` | Merchandiser Orders Board | Desktop (1280px) | Textile Atelier ivory palette, 4 health badges, needle-tick milestone tracks, search & severity sort |
| `02_merchandiser_board_mobile.jpg` | Merchandiser Orders Board | Mobile (360px) | Compact stacked card elevation, bottom navigation bar, live status chips |
| `03_merchandiser_outbox.png` | Outbox Simulator | Desktop (1280px) | Simulated dispatched buyer delay notices with timestamp & message payload |
| `04_supervisor_home_desktop_filters.png` | Supervisor Floor Home | Desktop (1280px) | Dynamic stage filter pills (*All, Stitching, Finishing, Packing, Cutting*), search input, order grid |
| `05_supervisor_home_mobile_filters.jpg` | Supervisor Floor Home | Mobile (360px) | Compact `<LogoMark size={24} />` brand placement, instant search, stage toggle pills |
| `06_supervisor_updates_dialog.png` | Supervisor Updates Sheet | Desktop (1280px) | Bottom sheet modal displaying live offline queue outbox status |
| `07_buyer_portal_desktop.png` | Buyer Status Portal | Desktop (1280px) | Factory provenance (*"Status updates from Company A"*), verified delay notice, milestone checklist |
| `08_buyer_portal_mobile.jpg` | Buyer Status Portal | Mobile (360px) | Non-wrapping quantity and ex-factory dates, 2-tier mobile header, Excel download |
| `09_login_page_demo_options.png` | Authentication & Demo Logins | Desktop / Mobile | Clean credential inputs, unified demo buttons for Priya, Murugan, Selvi, and Hannah |
| `10_supervisor_role_switcher_mobile.jpg` | Role Switcher Dropdown | Mobile (360px) | Viewport-clamped portal positioning, zero screen bleed, 1-click role swapping |

---

### Automated Journey Captures (Original P00–P36 Test Run)
* `j1_sup_*`: Supervisor floor onboarding, count update stepper, offline queue, and reconnected sync states.
* `j2_merch_*`: Merchandiser board, warning inbox, detail review, and confirmation flows.
* `j3_setup_*`: 4-step order creation stepper (Metadata, Quantities, Dates, Review).
* `j4_buyer_*`: Buyer token entry, order list, and detailed milestone status.
* `j5_change_date_sheet_*`: Ex-factory date change modal with reason validation.
