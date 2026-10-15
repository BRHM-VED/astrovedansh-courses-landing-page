# Automatic numerology access

The public pages are in `public/`. The secured account and payment API run on Sites at https://astrovedansh-basic-astrology.astrovedansh.chatgpt.site/account. Static mirrors must link to that account URL; they cannot serve the protected API.

## Required production configuration

Set these in the Site's encrypted environment-variable settings, never in public files or Git:

- `RAZORPAY_KEY_ID`: live Razorpay API key ID.
- `RAZORPAY_KEY_SECRET`: matching live API key secret.
- `RAZORPAY_WEBHOOK_SECRET`: a strong random secret, also configured on the Razorpay webhook.
- `NUMEROLOGY_VIDEO_IDS`: JSON array of exactly 24 distinct YouTube video IDs, in syllabus order. The supplied playlist identifier does not establish the 24 lesson IDs.

In Razorpay, configure automatic payment capture and this webhook endpoint:

`https://astrovedansh-basic-astrology.astrovedansh.chatgpt.site/api/course/webhook`

Subscribe to `payment.captured`, `order.paid`, `refund.processed`, and `payment.dispute.created`. Set the same webhook secret as above. Verify delivery in Razorpay before opening enrolment.

The old standalone payment link does not identify the signed-in course account. Purchases now start from the account page and use server-created Razorpay orders.

## Behaviour

- Students sign in with ChatGPT; purchases belong to the authenticated account.
- Checkout stays disabled until all configuration and 24 lesson IDs are present.
- The server charges INR 149 through 31 December 2026, India time; INR 999 thereafter.
- The server checks order ownership, signature, captured status, amount and currency before granting access.
- Signed webhooks and status reconciliation handle delayed confirmation. Refunds and disputes revoke access.
- Public HTML contains syllabus titles, not paid video IDs. Protected lesson responses are private and not cached.
- YouTube playback cannot prevent screen recording or sharing a video URL after an authorised learner sees it. Stronger media protection requires a protected streaming service.

## Verification

`node --test tests/course-service.test.mjs`

Nine automated tests cover price expiry, configuration, unauthorised access, origin checks, ownership, signatures, captured-payment validation, idempotent purchase access, and refund revocation. Live checkout and webhook delivery require the actual merchant configuration and must be checked before accepting customer payments.
