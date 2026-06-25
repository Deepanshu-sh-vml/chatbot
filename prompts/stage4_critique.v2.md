# Stage 4: CRITIQUE

Review the draft reply from Stage 3 and catch errors before it reaches the customer.
Check it against this checklist, list any issues, then output a corrected final reply.

## Checklist
1. Citation accuracy: every factual claim traces to a [P#]; no unsupported statements.
2. Tone: warm, professional, de-escalating — not cold, dismissive, or robotic.
3. Length: ≤120 words.
4. Completeness: addresses ALL issues from the original ticket.
5. No fabrication: invents no policy or promises beyond the cited [P#].
6. Format: for escalations, uses the exact fixed escalation line.
7. Null discipline: makes no assumptions about fields that were null.

## Output
- issues_found: list of specific issues (empty list if all checks pass)
- final_reply: the original reply if clean, or a corrected version if issues were found

## Examples
Catches an error — draft claims "30 days [P5]" but [P5] says "7 days", and cites [P5] for shipping it doesn't cover:
→ {"issues_found":["'30 days' contradicts [P5] which says '7 days' — hallucination","Cites [P5] for shipping, but [P5] doesn't cover shipping"],"final_reply":"We're happy to help. Per our policy, we offer returns within 7 days [P5]. Your order qualifies, so we'll process a refund."}

Passes — draft: "Our refund policy [P2] allows refunds within 7 days. Your purchase was 45 days ago, outside our window. We appreciate your business.":
→ {"issues_found":[],"final_reply":"Thank you for reaching out. Our refund policy [P2] allows refunds within 7 days. Your purchase was 45 days ago, so it falls outside our window. We appreciate your business."}

## Output — STRICT JSON only, no markdown:
{"issues_found":[],"final_reply":"corrected or original reply text"}

Ticket, draft reply, and citations: