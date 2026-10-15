# AstroVedansh Basic Vedic Astrology Course

A responsive course landing page with complete Hindi/Hinglish and English versions.

## Content source

Course structure and learning materials are based on the supplied `Vedic_Astrology_Basic_Course_3_Month_Curriculum-1.pdf` (12 pages).

Confirmed fee: INR 12,000 less INR 2,000 discount = INR 10,000, supplied by the owner on 11 September 2026.

All five payment links point to the exact owner-supplied Razorpay URL: https://rzp.io/rzp/0IzCNyC

Confirmed course bonus: one year of AstroTry astrology software access, valued at INR 12,000, included at no extra cost. Offer and supplied promotional image provided by the owner on 11 September 2026. The app link is https://play.google.com/store/apps/details?id=com.FinalAstroTry.app. No activation process or additional subscription benefits have been assumed.

## Implementation

- Static HTML and shared CSS in `dist/`. `index.html` is Hindi/Hinglish; `english.html` is English.
- Header language buttons switch the entire page with normal links; no JavaScript is required.
- After changing the Hindi page, run `python scripts/sync-language-pages.py` to regenerate English from `translations/en.json`. The authoring helper requires lxml.
- Native details/summary elements for the 12 curriculum weeks and nine FAQs.
- Responsive header, course enrolment card and mobile payment bar.
- The course headline, description and enrolment details appear first. The owner-supplied YouTube video follows below them on mobile and desktop, and loads lazily as visitors scroll. The native player supports inline playback and fullscreen, with a direct YouTube link as a fallback.
- An About Me section uses the supplied portrait unchanged; responsive cropping is applied only in CSS. Biography is based on owner-provided context: founder role, astrology/numerology practice, ICAS qualifications and areas of study.
- The AstroTry bonus appears in the opening course details, a dedicated section before enrolment and the price card; the supplied image links to Google Play.
- Footer policy links use the three exact URLs supplied by the owner. Policy documents are hosted externally.
- Mulish is the primary font, with Noto Sans Devanagari for Hindi glyphs and system fallbacks.
- The supplied AstroVedansh logo replaces the header star; circular cropping is applied only in CSS. The source image is unmodified.
- Gold, teal and violet emphasis highlights important course details, benefits and prices.

## Details to confirm for future updates

Batch date/time, recording access duration were not supplied. The owner supplied an external refund policy URL on 11 September 2026; policy terms have not been restated or assumed here. No such promises or fabricated testimonials, countdowns, seat limits, or guaranteed outcomes have been added. Certificate is described as academy-issued.

## Validation

Both language pages are checked for unique IDs, all 12 curriculum weeks, nine FAQs, language navigation, local assets, original-logo integrity, five exact Razorpay links per language, consistent pricing, and complete English translation including accessibility labels and metadata. This update also checks the video ID, the original portrait, About Me navigation and all three policy links. No browser QA was requested or performed.

## Course copy update — 12 September 2026

Rewrote both language versions around the beginner learning goal, a 7-step chart-reading method, guided practice, a 2–3 page final basic analysis, course inclusions and clear enrolment copy. Kept the owner-selected opening headline and the video below the course introduction. The curriculum, fee, discount, software bonus and external links are unchanged. No new dates, access terms, outcome guarantees or testimonials were introduced.

## Classical study and future paths — 15 September 2026

Rewrote the page in both languages around classical texts, reasoning and chart practice, retaining the owner-selected opening headline. Added reasons to learn, six learner groups, source texts, further study and work paths, and clearly labelled hypothetical gross revenue examples. Historical context for Jyotisha among the six Vedangas is attributed inline to IGNCA’s Vedic Heritage Portal: https://vedicheritage.gov.in/vedangas/. The copy distinguishes the historical timing context from this course’s Parashari birth-chart focus. It makes no claim of scientific proof or guaranteed earnings. All earning figures are assumed arithmetic, not market rates or student results. Advanced study and guided practice precede professional consultation work. Pricing, bonus, owner images, video order, payment and policy destinations remain intact.
