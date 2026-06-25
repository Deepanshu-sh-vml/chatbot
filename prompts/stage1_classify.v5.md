# Stage 1: CLASSIFY

Classify the support ticket into exactly ONE category:
- billing: payments, refunds, charges, money back, subscriptions, pricing, proration
- account: passwords, login, cancellations, plan changes, profile
- technical: crashes, bugs, features not working, performance, SHIPPING & DELIVERY (timing, expedited, international)
- other: ONLY pure praise, spam, or genuinely no support request

## Category clarifications
- ANY mention of a refund, charge, or money back → billing
  (even if the product is damaged or the request might be escalated later).
- Shipping / delivery questions (timing, expedited, international) → technical.
- "other" is NOT a fallback for valid requests you're unsure about — only use it
  for pure praise, spam, or messages with no actual support topic.

## Rules
- NEVER invent categories — use only the four above.
- Multi-intent (e.g. "can't login AND overcharged") → pick the PRIMARY issue.
- Always pick ONE category, no hedging.

## Confidence (0.0–1.0) — BE HONEST about ambiguity
- 1.0 = crystal clear, single intent
- 0.8–0.9 = clear primary, minor secondary signal
- 0.6–0.7 = ambiguous / could fit two categories
- <0.6 = highly unclear
RULE: If the ticket could reasonably fit TWO categories, confidence MUST be below 0.7.
Ambiguity signals: mentions both money AND logistics; multiple topics; unclear primary intent.

## Examples
"Charged twice for my annual subscription. Help?"
→ {"category":"billing","confidence":0.95,"reason":"Duplicate charge = billing"}

"My login doesn't work and I can't see my invoices"
→ {"category":"account","confidence":0.6,"reason":"Multi-intent: login (account) + invoices (billing); ambiguous"}

"I want to ship internationally — how much and how long?"
→ {"category":"technical","confidence":0.6,"reason":"Ambiguous: cost (billing) vs delivery logistics (technical)"}

"My order arrived damaged, I want a refund."
→ {"category":"billing","confidence":0.85,"reason":"Mentions refund/money → billing"}

## Output — STRICT JSON only, no markdown:
{"category":"billing|account|technical|other","confidence":0.0,"reason":"brief"}

Ticket to classify: