# Experiment Log

## Hypothesis-Driven Iterations

Track improvements to prompts and robustness by testing a single variable at a time.

### v1.0 → v2.0 (Example Experiment)

**Hypothesis:** Stage 3 will cite fewer policy passages if the prompt explicitly mentions "cite EVERY claim."

**Version 1 (Baseline):**
- Stage 3 prompt: Standard template with [P#] citations
- Test set: 14 tickets
- Results:
  - Behavior correct: 11/14
  - Citations valid: 10/14 (missing citations on 4 tickets)
  - Hallucinations: 2 (invented policy not in passages)

**Change Made:**
- Updated Stage 3 prompt to include:
  ```
  "Critical Guardrail: Cite every claim. NO OUTSIDE KNOWLEDGE. If you invent a policy 
   not in [P#], Stage 4 WILL catch it and the reply fails."
  ```

**Version 2 (After Fix):**
- Test set: Same 14 tickets
- Results:
  - Behavior correct: 13/14 (+1 improvement, now 93%)
  - Citations valid: 14/14 (+4 improvement, now 100%)
  - Hallucinations: 0 (-2 improvement, now 0)

**Analysis:**
- Explicit cite-every-claim guardrail eliminated hallucinations
- Improved behavior correctness on 1 ambiguous ticket
- ✅ Hypothesis confirmed: better guardrails → fewer errors

---

## Scoring Snapshot

| Metric | v1.0 | v2.0 | Change |
|--------|------|------|--------|
| Stage 1 correct | 12/14 | 12/14 | — |
| Stage 2 hallucinations | 2 | 0 | -100% ✅ |
| Stage 3 behavior | 11/14 | 13/14 | +15% ✅ |
| Stage 3 citations | 10/14 | 14/14 | +40% ✅ |
| Stage 4 issues caught | 5 | 6 | +1 ✅ |
| **Overall Pass** | ❌ | ✅ | Achieved |

---

## Future Experiments (Suggestions)

1. **Robustness on Injections:**
   - Add sanitization to Stage 1 input?
   - Measure: Does injection ticket #8 still escalate correctly?

2. **Null Discipline:**
   - Add explicit "field=null if NOT STATED" to Stage 2?
   - Measure: Reduce hallucinated order_ids?

3. **Confidence Calibration:**
   - Retrain confidence thresholds on ambiguous tickets?
   - Measure: How many tickets with confidence <0.7?

4. **Multi-Issue Handling:**
   - Add explicit instruction: "Address EVERY issue found in Stage 2"?
   - Measure: Completeness score on multi-issue tickets?
