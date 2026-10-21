# Offer / copy staging — 21 October 2026

## Implemented
- Updated bilingual homepage/category/service copy in the existing ivory–maroon layout.
- Config/catalog.json is the pricing source for generated homepage, report, consultation and four booking pages, plus both course pages. Edit templates/pricing then run `python3 scripts/build-catalog.py`; `--check` detects stale output. External checkout settings remain outside this repository.
- Perfect Timing section preserves the real single-question ₹349 destination and genuine sample PDF.
- /offer-review.html (noindex, no homepage link) shows proposed ₹649/₹1,047 packs and ₹3,799 consultation pilot, explicitly inactive. No fake purchase links. Savings calculated from configured single price.
- Offer flags require business approval and verified checkout. Timing offers also require chart eligibility and delivery scope. The consultation pilot remains blocked until booking conditions and measurement are integrated.
- Optional post-delivery Expert ₹1,100 upsell fragment prepared in templates/report-followup.html. NOT connected or sent: this repo has no delivery webhook/consent system.
- Local privacy-safe event queue and CustomEvent hooks: page_view, service_category_click, timing_package_selection, consultation_option_selection, outbound_product_click, language_selection. No third-party collector or advertising transmission; no form/birth details or URL queries captured.

## Pricing consistency and checkout audit
| Product | Hub / page | Actual destination / limitation |
|---|---:|---|
| Timing single | ₹349 | External page rechecked today: ₹349. No bundle SKU verified. |
| Timing 2 | ₹649 proposed | Disabled; approval, eligible questions, same-chart rule, fulfillment and exact checkout needed. |
| Timing 4 | ₹1,047 proposed | Disabled; approval, eligible questions, same-chart rule, fulfillment and exact checkout needed. |
| Career | ₹349 requested | External page rechecked today still ₹449. Must resolve before deploying new offers. |
| Name | ₹501 | Owner-approved display; WhatsApp inquiry, no integrated checkout to verify. |
| Milan | ₹2,999 | WhatsApp inquiry; no integrated checkout to verify. No new Guna-matching claim. |
| Audio | ₹999 | Existing 10–15min WhatsApp recorded-audio request. |
| Expert | ₹1,100 | Existing 20–25min live booking request. |
| Personal | ₹2,100 | Existing 30min live booking request. |
| Detailed | ₹4,200 | Existing 60min booking request. ₹3,799 proposal remains inactive. |
| Foundation | ₹10,000 | Existing checkout previously verified ₹10,000; supplied brief ₹15,000 conflicts. No payment setting changed. |
| Advanced | ₹35,000 requested | No verified matching checkout. Not added. |
| Predictive Numerology | ₹21,000 requested | No verified matching checkout. Not added. |
| Astrology Report | ₹399 requested | No verified destination. Not added. |
| Free Numerology | ₹999 → ₹0 with NUMEROPRO | Existing coupon script/process preserved. |
| InBhakti | — | Missing verified URL. Not added. |

161 anchors audited in docs/offer-link-audit.csv. Existing destinations and images preserved. All local target files exist. External Timing and Career pages inspected in browser; no payment submitted. Course checkout and payment receipts were not retested transactionally.

## Verification
- English and Hindi homepage checked at 320/360/390/430 content widths: no document horizontal overflow.
- Native language switching exercised, offer review has two truly disabled purchase controls.
- Static generated-price consistency check passed.
- Offer guard tests: enabling unapproved offers fails; proposed prices absent from customer pages.
- Click event test confirms expected event names, no personal query values, and no invented purchase/booking conversions.
- Existing payment and booking scripts unchanged. No real orders or messages sent.

## Backend requirements / deployment checklist
1. Approve or reject ₹649 two-question pack and ₹3,799 60-minute pilot.
2. Confirm ₹1,047 bundle, eligible question list, same-birth-chart rule, one-versus-multiple-PDF format, delivery scope/time and discount stacking.
3. Provide approved bundle SKUs/checkouts and backend access; verify exact amounts via payment-provider test mode before enabling.
4. Resolve Career ₹349/₹449 and Foundation ₹10,000/₹15,000.
5. Provide verified analytics destination and consent wiring. Purchase/booking/revenue/AOV/RPV require server-confirmed events, unique transaction-ID deduplication and attribution; none is simulated in the browser.
6. Wire delivery-confirmed upsell only in an eligible consented channel, not utility WhatsApp messages.
7. Review screenshots and approve production deployment. This branch is staging only.
