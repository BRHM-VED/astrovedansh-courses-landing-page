# Daily journal publication

The owner reauthorized daily article publication on 22 October 2026. The existing daily task is `6ad358af4bd081919289fa557eedf7a9`, scheduled around 09:00 Asia/Calcutta. Continue it without routine per-run confirmation; platform authentication and approval requirements still apply.

## Production source

The customer-facing website is `https://courses.astrovedansh.org`. Its production source is current `main` in `BRHM-VED/astrovedansh-courses-landing-page`. Vercel serves `public/` according to `vercel.json`. Start with the latest main, preserve unrelated changes and use a guarded branch update. An older Sites checkout must never replace this source. The existing Sites publication is a separate mirror, not the canonical deployment gate.

## Publication batch

1. Read the current journal manifest, dated batches and relevant existing articles. Resume an existing batch for the current India date instead of allocating duplicate URLs.
2. Prepare ten substantial Hindi lessons under the owner's editorial standard. Expand an existing URL when the search intent overlaps; report the new/expanded counts accurately. Research primary texts and distinguish text, practitioner method and original teaching interpretation. Never invent sources or client outcomes.
3. Save the article assets as `content/lessons-YYYY-MM-DD-a.json`, `-b.json` and `-c.json`, and retain the supporting research record. Use the existing article schema and optimized reusable cover assets.
4. Run `python3 scripts/build-journal-lessons.py --date YYYY-MM-DD`, then `python3 scripts/build-newsletter-feed.py`, then `python3 scripts/validate-journal-batch.py YYYY-MM-DD`. Confirm the batch is stable on a second render. Original publication dates and feed GUIDs must stay unchanged for expanded articles.
5. Review article content, internally consistent example charts, links and a representative mobile page. Fix actual failures. Keep homepage, product pricing, funnel, booking integrations and customer data unchanged.
6. Publish the exact validated content to GitHub main and verify the corresponding Vercel deployment result. Report actual titles, URLs, dates and deployment evidence. Saving files or committing code alone is not proof of live publication.

If a run is blocked, retain its dated work and report the exact blocker. Do not report unpublished work as live, backdate missed batches, or disable the recurring schedule merely because an individual article/build failed. Resume the same batch after the blocker is resolved.
