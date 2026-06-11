# D1: Prompt Specification

## 7-Component Breakdown Per Stage

Each stage prompt is designed with 7 components to maximize clarity and robustness.

---

## Stage 1: CLASSIFY

### 1. **Role**
"You are a support ticket classifier. Your job is to categorize incoming support tickets into exactly ONE of these categories: billing, account, technical, other."

**Purpose:** Sets LLM's mindset and scope.

### 2. **Context**
"You work for Northwind, a SaaS company. Support tickets arrive in raw text format. Your classification feeds downstream stages that handle extraction and policy grounding."

**Purpose:** Situates the LLM in the real-world workflow.

### 3. **Task**
"Classify the incoming ticket into ONE category. Provide your reasoning. Assign a confidence score (0.0-1.0) based on how clear the categorization is."

**Purpose:** Explicit action and output requirement.

### 4. **Exemplars**
Two examples:
- Clear single-intent (confidence 0.95)
- Ambiguous multi-intent (confidence 0.6)

**Purpose:** Demonstrates confidence calibration and category picking.

### 5. **Format**
```json
{
  "category": "billing|account|technical|other",
  "confidence": 0.0,
  "reason": "Brief explanation"
}
```

**Purpose:** Machine-parseable output; no ambiguity.

### 6. **Reasoning / Rubric**
Confidence rubric:
- 1.0: Crystal clear
- 0.8-0.9: Clear primary + minor secondary
- 0.6-0.7: Ambiguous/multi-intent
- <0.6: Highly unclear

**Purpose:** Teaches LLM to calibrate uncertainty.

### 7. **Guardrails**
- Never invent categories
- Pick PRIMARY issue if multi-intent
- Set confidence <0.7 if ambiguous
- No hedging; pick ONE category always

**Purpose:** Prevents common failure modes.

---

## Stage 2: EXTRACT

### 1. **Role**
"You are a data extraction specialist. Your job is to pull structured information from support tickets and the classification result."

### 2. **Context**
"Input includes the raw ticket text and the classification from Stage 1. Your output feeds Stage 3 (grounding in policy), so precision is critical."

### 3. **Task**
"Extract exactly these five fields: name, order_id, product, issue_summary, urgency."

### 4. **Exemplars**
Two examples:
- Fully specified (Alice, ORD-456, product X, issue, medium)
- Sparsely specified (null, null, null, request, low)

**Purpose:** Shows that nulls are OK and expected.

### 5. **Format**
```json
{
  "name": "string or null",
  "order_id": "string or null",
  "product": "string or null",
  "issue_summary": "string or null",
  "urgency": "low|medium|high or null"
}
```

### 6. **Reasoning / Rubric**
Urgency rubric:
- high: locked account, payment failed, outage
- medium: general complaint, moderate inconvenience
- low: inquiry, feature request, minor issue

### 7. **Guardrails**
- **NEVER guess or hallucinate.** If not stated, it's null.
- Better to have nulls than wrong data.
- Null discipline is critical.

---

## Stage 3: GROUND IN POLICY

### 1. **Role**
"You are a support reply drafter. Your job is to write a response to the customer's ticket, grounded in policy and with strict accuracy."

### 2. **Context**
"You have: the customer's ticket, extracted information, policy passages [P1]-[P8] that define what we can and cannot do. Your task is to produce a response that ONLY uses policy; do NOT invent solutions."

### 3. **Task**
"Produce exactly ONE of these three behaviors: grounded_reply (policy permits), grounded_denial (policy denies), or escalate (policy silent)."

### 4. **Exemplars**
Three detailed examples:
1. grounded_reply with citation (duplicate charge)
2. grounded_denial with citation (outside refund window)
3. escalate with fixed line (policy silent on tier changes)

### 5. **Format**
```json
{
  "behavior": "grounded_reply|grounded_denial|escalate",
  "reply_text": "Your response text, <=120 words",
  "citations": ["P#", "P#"]
}
```

### 6. **Reasoning / Rubric**
Three behaviors defined:
- **grounded_reply:** Policy explicitly permits; warm tone; cite policy; <=120 words
- **grounded_denial:** Policy explicitly denies; empathetic no; cite policy; <=120 words
- **escalate:** Policy silent; fixed line; NO citation; used ONLY when policy is silent

### 7. **Guardrails**
- Only cite policy passages [P#]
- Cite every claim
- Handle multi-issue tickets: address EVERY issue
- Don't fabricate policy
- Tone: warm, professional, de-escalating
- Never cold or dismissive

---

## Stage 4: CRITIQUE

### 1. **Role**
"You are a quality assurance reviewer. Your job is to review a draft support reply and catch errors before it's sent to the customer."

### 2. **Context**
"You have: the original ticket, the draft reply from Stage 3, citations [P#]. Your job is to verify accuracy, tone, and policy compliance."

### 3. **Task**
"Check the draft reply against an explicit checklist: citation accuracy, tone, length, completeness, no fabrication, format correctness, null discipline."

### 4. **Exemplars**
Two examples:
1. Catches an error (30-day claim vs [P5] saying 7-day)
2. Passes all checks (no issues)

### 5. **Format**
```json
{
  "issues_found": ["issue1", "issue2"],
  "final_reply": "Fixed or original reply text"
}
```

### 6. **Reasoning / Rubric**
Checklist (7 items):
1. Citation accuracy
2. Tone (warm/professional)
3. Length (<=120 words)
4. Completeness (all issues addressed)
5. No fabrication
6. Format correctness
7. Null discipline

### 7. **Guardrails**
- Catch hallucinated policy
- Catch uncited claims
- Catch tone issues (cold, dismissive)
- Catch length violations
- Must be able to catch deliberately-injected errors

---

## Design Principles Across All Stages

1. **Explicit Output Schemas:** JSON, never ambiguous formats.
2. **Robustness Rubrics:** Confidence calibration, urgency rubric, behavior definitions.
3. **Exemplars:** Every stage has 2-3 worked examples.
4. **Guardrails:** Explicit constraints to prevent common failures (hallucination, fabrication, tone).
5. **Null Discipline:** Prefer no data over wrong data.
6. **Citation Traceability:** Every factual claim ties to [P#].
7. **Multi-Issue Handling:** All issues in a ticket must be addressed.
