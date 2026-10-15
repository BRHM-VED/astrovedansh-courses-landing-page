# Numerology: payment to private email access

## Current state

The account page now uses email-only access, without ChatGPT sign-in. The implementation is staged and checkout is disabled. No merchant credentials, email sender or 24 lesson IDs are configured. Automated fixture tests are not a successful live checkout or live email delivery test.

The old Razorpay API keys do not need to be regenerated or supplied for this flow.

## Required setup

Configure through encrypted Sites runtime environment settings:

- `RAZORPAY_WEBHOOK_SECRET`: separate secret also set on the new Razorpay webhook.
- `RAZORPAY_ACCOUNT_ID`: exact merchant account identifier from a verified provider event.
- `RESEND_API_KEY`: transactional sending credential.
- `COURSE_EMAIL_FROM`: address on a verified sending domain. Do not use an unverified Gmail address as the sender.
- `COURSE_TOKEN_SECRET`: cryptographically random server secret of at least 32 characters.
- `NUMEROLOGY_VIDEO_IDS`: JSON array of all 24 distinct YouTube IDs in syllabus order.
- `COURSE_SOURCE_KIND` and `COURSE_SOURCE_ID`: exact provider-owned source entity and ID, after the verification below.
- `COURSE_SOURCE_VERIFIED=true`: set only after a signed real event proves the source mapping.
- `COURSE_EMAIL_ENABLED=true`: set only after all configuration, delivery and playback tests succeed.

Webhook endpoint:

https://astrovedansh-basic-astrology.astrovedansh.chatgpt.site/api/course/webhook

Configure captured-payment events appropriate to the actual payment product and `refund.processed` and `payment.dispute.created`.

## Payment Page compatibility is NOT established

The supplied URL is https://rzp.io/rzp/rNERqwqw. Its real webhook schema has not been inspected. A Payment Page and a Payment Link are different products. Do not assume their webhook payloads have the same entity fields.

The strict adapter in `lib/email-course.mjs` only accepts a matching provider-owned `payload.payment_link.entity` or `payload.payment_page.entity`. The `payment_page` branch is a reserved adapter, NOT a claim that this merchant's page emits that entity. It must be confirmed or replaced based on observed provider data before activation. If the merchant's event lacks a trusted course identifier, the current integration cannot safely activate: change the payment product/configuration or implement a documented, verified provider-specific mapping first.

Do not relax this check to accept every INR 149 payment, customer-editable notes or a matching email. Other services share this merchant account.

## Access behaviour

A verified course payment records an entitlement for the payment email and sends a one-use link valid for 15 minutes. Tokens are stored hashed; the link uses a URL fragment so the token is not sent in server request URLs. The recipient presses Open my classes to consume it, avoiding consumption by email GET scanners. This creates a Secure, HttpOnly, SameSite=Strict session for 30 days. All lesson requests check current purchase status. Refund/dispute events create revocation tombstones, including when delivered before the payment event.

Replayed webhooks reuse the same email idempotency key. Failed email delivery returns a retryable response; expired unsent tokens are renewed on retry. A rate-limited request form sends fresh links only to purchased emails, with the same public response for unknown emails. Disable email link tracking at the sender so fragment links remain intact.

The fixed Razorpay page has the owner's INR 149 offer. Checkout is hidden after the offer expires on 31 December 2026 (India time) until the merchant page and pricing flow are updated. Public course pricing then shows INR 999. Server validation uses the payment creation time for delayed events.

YouTube is not DRM: authorised viewers can extract/share video URLs or record the screen. The email link itself can also be forwarded before first use. Stronger identity/media protection needs additional controls.

## Validation and hosting

`node --test tests/email-course.test.mjs`

The new suite covers readiness, webhook signatures, merchant/course/amount matching, one-time tokens, expiry, secure cookies, unauthorised lessons, refunds, request throttling and email retry. Actual Razorpay events, sender delivery and all 24 videos still require live verification before activation.

Public files live in `public/`. Account and payment APIs run on Sites. GitHub/Vercel is a static mirror pointing course buttons to the Sites account URL; do not deploy the server there without adapting the runtime and storage.

## Superseded: free coupon access (15 October 2026)

The owner cancelled paid enrolment and email access. The active course flow now displays INR 999 and applies the public NUMEROPRO coupon for a full INR 999 discount, total INR 0. It requires no payment, authentication or email delivery. `/account` redirects to the coupon section; `/api/course/*` returns 410 and performs no payments or email operations. Prior backend modules remain archived source only and are not routed.

The public player uses the owner's originally supplied playlist `PLN80wspGZ5mw`. Playback and all 24 video IDs remain unverified; supply the complete playlist URL to repair unavailable playback. The coupon is a public promotion, not a security boundary. No new expiry date has been assigned.
