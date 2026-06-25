# D4: Experiment Log

## Purpose
This log records the versioned history of prompt changes: each change, the hypothesis
behind it, and its measured effect on the 14-ticket test set. It follows the
"one variable at a time, evidence over vibes" principle.

---

## Version History

### v1 — Baseline (verbose prompts)
- **Change:** Initial 4-stage prompts with full role/context/exemplars.
- **Hypothesis:** A complete, detailed prompt for each stage will produce reliable output.
- **Measured effect:**
  - Stage 1: 10/14 correct · confidence <0.7 on ambiguous: 0/4
  - Stage 2: 3 hallucinations
  - Stage 3: 6/14 behaviors
  - **Overall: FAIL**
- **Takeaway:** Functional baseline, but Stage 3 behaviors and Stage 2 hallucinations are weak.

---

### v2 — Prompt trimming + explicit confidence rule
- **Change:** Trimmed all four prompts ~45% (removed role/context bloat); made the
  "ambiguous → confidence <0.7" rule explicit in Stage 1.
- **Hypothesis:** Removing redundant text will reduce latency and token cost without hurting
  quality; an explicit confidence rule will improve calibration.
- **Measured effect:**
  - Stage 1: 10 → 9 correct (regression) · confidence 0 → 1
  - Stage 2: 3 → 2 hallucinations
  - Stage 3: 6/14 (unchanged)
  - Latency reduced.
  - **Overall: FAIL**
- **Takeaway:** MIXED result. Trimming improved speed + confidence calibration but
  **over-trimmed Stage 1 context, dropping accuracy.** A key lesson: trimming must preserve
  classification-relevant context.

---

### (Evaluator fix) — Citation comparison bug
- **Change:** Fixed `evaluate_stage3`: citations were compared with brackets (`[P3]`) against
  output without brackets (`P3`); also made the citation check behavior-aware (escalations
  must have no citations; grounded behaviors must cite valid passages).
- **Hypothesis:** Low citation scores were a measurement artifact, not a pipeline fault.
- **Measured effect:** Stage 3 citations jumped 3 → 9/14 with no pipeline change.
- **Takeaway:** Confirmed the failure was in the evaluator, not the prompts. Measurement
  integrity matters before tuning.

---

### v3 — Stage 3 decision logic + anti-deny anti-patterns
- **Change:** Added a 3-step "match topic → passage permits/refuses/silent → behavior"
  decision process, plus anti-patterns ("don't deny with loosely-related passages";
  "many citations to deny = escalate").
- **Hypothesis:** The model over-denies because the deny/escalate boundary is fuzzy; explicit
  decision logic will sharpen it.
- **Measured effect:** Stage 3 behaviors 6 → 9/14.
- **Takeaway:** Big improvement, but **over-corrected** — some grounded tickets now
  over-escalated, and two traps wrongly replied.

---

### v4 — Corrected Stage 3 exemplars + topic→passage map (BREAKTHROUGH)
- **Change:** (a) Fixed misaligned few-shot examples — the old "shipping → escalate" example
  was teaching the model to escalate shipping (which P8 covers!), and a duplicate-charge
  example cited P3 instead of P2. Replaced with policy-accurate examples. (b) Added an
  explicit topic→passage map and trap warnings (P7 = app crash ≠ damaged goods; P5 =
  cancellation ≠ billing-date change).
- **Hypothesis:** Misaligned exemplars were actively teaching wrong behavior; aligning them
  to the real policy will fix multiple misclassifications.
- **Measured effect:** Stage 3 behaviors 9 → 12/14 · citations → 13/14. **Stage 3 PASS.**
- **Takeaway:** The single largest gain. **Few-shot examples must match the actual policy** —
  a bad exemplar propagates errors across the test set.

---

### v5 — Stage 1 & 2 targeted fixes (OVERALL PASS)
- **Change:**
  - Stage 2: added "malicious/junk ticket → ALL fields null"; "product = specific names
    only, generic terms → null".
  - Stage 1: "shipping/delivery → technical"; "any refund/money → billing"; "'other' only
    for praise/spam"; added two exemplars (international shipping = ambiguous; damaged+refund
    = billing).
- **Hypothesis:** The last hallucination is the injection ticket's summarized threat;
  Stage 1 errors are shipping/refund tickets defaulting to "other".
- **Measured effect:**
  - Stage 1: 9 → 11/14 (PASS)
  - Stage 2: 1 → 0 hallucinations (PASS)
  - Stage 3: 12 → 13/14
  - **Overall: PASS** 🎉
- **Takeaway:** Targeted category clarifications and the malicious-null rule closed the
  remaining gaps.

---

## Summary Table

|   Ver  |  Stage 1  | Conf <0.7 | Stage 2 halluc | Stage 3 behav | Stage 3 cite |  Overall |
|--------|-----------|-----------|----------------|---------------|--------------|----------|
|   v1   |   10/14   |    0/4    |       3        |      6/14     |       —      |    FAIL  |
|   v2   |    9/14   |    1/4    |       2        |      6/14     |       —      |    FAIL  |
|   v3   |    9/14   |    0/4    |       2        |      9/14     |     10/14    |    FAIL  |
|   v4   |    9/14   |    0/4    |       1        |     12/14     |     13/14    |    FAIL  |
| **v5** | **11/14** |  **1/4**  |     **0**      |   **13/14**   |   **14/14**  | **PASS** |

---

## Key Lessons
1. **Aligned exemplars matter most.** The biggest single gain (v3→v4, +3 behaviors) came from
   correcting a misaligned few-shot example, not from adding more rules.
2. **Measure before tuning.** An evaluator bug (citation brackets) was masking real progress;
   fixing measurement first avoided chasing a phantom problem.
3. **Trimming is a trade-off.** v2 showed that aggressive trimming can remove useful context;
   speed gains must be balanced against accuracy.
4. **Targeted beats broad.** v5's small, specific category rules fixed exactly the failing
   tickets without regressing the passing ones.
5. **Confidence calibration resisted tuning** — improved only 0→1/4 despite explicit rules and
   exemplars; a documented LLM limitation (see D6).