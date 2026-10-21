# Approved service pricing and combos — 21 October 2026

## Published scope

Preserved the existing ivory/maroon design, images, language preference, external course/report checkout links, customer data and booking number. No new dependency or database migration.

- `config/catalog.json`: approved standalone services and bundles, stable product IDs, fulfilment items, durations, modes, upgrade mapping and contact configuration.
- `scripts/pricing_components.py`, `scripts/build-catalog.py`: generate static cards, pricing overview, pricing page and browser booking catalog from the same prices.
- Homepage (`index.html`, `english.html` and templates): report entry price ₹299, live ₹999, audio ₹799, View All Plans link and a concise ₹299–₹3,499 overview. Replaced the repeated four-row consultation list with this overview.
- Consultation listing and four existing booking routes: new prices, Complete Consultation naming, optional relevant upgrades; existing routes retained.
- Reports: Astrology Report ₹299, Perfect Name ₹399, report combo link; legacy Name/Milan request deep links still work with fee and plan in the request.
- `pricing.html`: four guidance filters, all four combos and all six standalone services. Exact savings; genuine standalone sum strike-throughs; Complete Life Guidance marked Recommended. Standalone shortcut keeps lower-priced plans accessible.
- `book-guidance.html`, `booking-catalog.js`, `booking-model.js`, `consultation.js`: reusable form, selected-plan summary, explicit upgrade/undo, plan-specific required fields, validated dates and WhatsApp handoff.
- `guidance-plans.css`, `pricing-plans.js`: scoped layout and filtering.
- `conversion-events.js`: plan selection, filter, optional upgrade and WhatsApp handoff events. No birth/contact/form data in analytics. No fake purchase event.

| Standalone service | Fee | Format |
| --- | ---: | --- |
| Astrology Report | ₹299 | Personalized written kundli-based report |
| Perfect Name Report | ₹399 | Personalized numerology-based name report |
| Vedansh Audio Analysis | ₹799 | 10–15 minute recorded WhatsApp voice note, not a live call |
| Expert Live Consultation | ₹999 | 20–25 minute live session with team astrologer |
| Vedansh Personal Consultation | ₹1,799 | 30 minute live session with Vedansh |
| Vedansh Complete Consultation | ₹3,199 | 60 minute live session with Vedansh |

| Combo | Individual total | Package fee | Savings | Item IDs |
| --- | ---: | ---: | ---: | --- |
| Report Combo | ₹698 | ₹499 | ₹199 | astrology_report, name |
| Audio Guidance | ₹1,098 | ₹899 | ₹199 | audio, astrology_report |
| Personal Guidance | ₹2,497 | ₹1,999 | ₹498 | personal, astrology_report, name |
| Complete Life Guidance | ₹3,897 | ₹3,499 | ₹398 | detailed, astrology_report, name |

## Fulfilment and payment boundaries

The deployed Vercel site is static. These services already use WhatsApp requests, not an online cart or service-order database. Each new plan sends a stable plan ID, exact package fee and one copy of every included item. Combo messages explicitly say not to bill included items separately. Upgrades require a click, can be undone, and preserve form details. Sending a form is not presented as a confirmed booking or successful payment.

No new gateway charge, customer record, automatic fulfilment record or order-confirmation email is created. Existing external checkouts and course payment/security code were left unchanged. Automatic online combo checkout and server-side order records require gateway/backend access and a separate verified deployment. Existing customer data was not accessed or modified.

There is no active tax computation for these WhatsApp services. The existing manual confirmation process remains: team confirms final payable amount and any applicable taxes before payment. No GST-included promise or invented tax rate was added. New report delivery format/timing is confirmed by the team rather than inventing a PDF or delivery deadline. The expert's 20-year experience statement is owner-provided in this approved task; no independent credential/certification claim was added.

Perfect Timing, Perfect Career, Perfect Milan, courses, apps and free resources retain their prior prices, links and terms. Earlier unapproved experiments remain inactive.

## Validation

- 41 Node tests passed, including all 10 plan handoffs, exact fees, fulfilment items, duplicate-submit guard, active upgrade/undo, alias routes, invalid forms, future birth dates and earliest booking dates. Tests use in-memory/mock integrations; no real payment or WhatsApp message sent.
- Catalog generator check, exact bundle arithmetic and inactive-offer activation guard passed.
- Local analytics privacy regression test passed.
- Static audit: 180 HTML pages and 33 scripts, no missing local references or JS syntax errors.
- Mobile: 360, 390 and 430 px; all ten plan booking views, homepage, Reports, Consultation and Pricing checked. Hindi and English UI, filtering, relevant fields, upgrade/undo, invalid form and preservation of entered name tested. No horizontal overflow.
- Desktop pricing page checked at 1363 px. Premium two-column combo grid on desktop; single-column combos on mobile.
- Existing service/course external payment destinations are preserved byte-for-byte; this task did not run an actual charge or verify production payment capture/order creation.
