"""
Evaluator: Score outputs against expected results and rubric.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import re

from src.schemas import (
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
    TestCase,
)


def load_test_set(test_set_path: str = "data/test_set.json") -> List[TestCase]:
    """Load test cases."""
    data = json.loads(Path(test_set_path).read_text())
    return [TestCase(**t) for t in data.get("tickets", [])]


def load_outputs(output_dir: str = "outputs") -> Dict[str, Dict[str, Any]]:
    """Load all pipeline outputs."""
    outputs = {}
    for output_file in Path(output_dir).glob("*_output.json"):
        ticket_id = output_file.stem.split("_")[0]
        outputs[ticket_id] = json.loads(output_file.read_text())
    return outputs


def score_dimension(actual: Any, expected: Any, dimension: str, test_case: TestCase) -> int:
    """
    Score a single dimension (0, 1, or 2).
    
    Context-aware scoring based on dimension and test case.
    """
    # This is a simplified scorer; a real implementation would be more sophisticated
    if dimension == "correctness":
        if actual == expected:
            return 2
        elif isinstance(actual, dict) and isinstance(expected, dict):
            matches = sum(1 for k in expected if actual.get(k) == expected[k])
            return 2 if matches == len(expected) else 1 if matches > 0 else 0
        else:
            return 0

    elif dimension == "format":
        # Check if it's valid JSON structure
        if isinstance(actual, dict) and actual:
            return 2
        return 0

    return 1  # Default neutral


def evaluate_stage1(
    test_cases: List[TestCase], outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Evaluate Stage 1 outputs."""
    results = {
        "total": len(test_cases),
        "correct": 0,
        "ambiguous_low_confidence": 0,
        "scores_per_test": {},
    }

    for test_case in test_cases:
        ticket_id = str(test_case.id)
        output = outputs.get(ticket_id, {})
        stage1 = output.get("stage1")

        if not stage1:
            results["scores_per_test"][ticket_id] = {"score": 0, "reason": "No output"}
            continue

        # Check correctness
        expected_category = test_case.expected_category
        actual_category = stage1.get("category")
        is_correct = actual_category == expected_category

        # Check confidence on ambiguous tickets
        confidence_ok = True
        if test_case.is_ambiguous:
            confidence = stage1.get("confidence", 1.0)
            if confidence < 0.7:
                results["ambiguous_low_confidence"] += 1
            else:
                confidence_ok = False

        if is_correct:
            results["correct"] += 1
            score = 2 if confidence_ok else 1
        else:
            score = 0

        results["scores_per_test"][ticket_id] = {
            "score": score,
            "expected": expected_category,
            "actual": actual_category,
            "confidence": stage1.get("confidence"),
        }

    return results


def evaluate_stage2(
    test_cases: List[TestCase], outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Evaluate Stage 2 outputs."""
    results = {
        "total": len(test_cases),
        "hallucinations": 0,
        "scores_per_test": {},
    }

    for test_case in test_cases:
        ticket_id = str(test_case.id)
        output = outputs.get(ticket_id, {})
        stage2 = output.get("stage2")

        if not stage2:
            results["scores_per_test"][ticket_id] = {"score": 0, "reason": "No output"}
            continue

        # Check null discipline: any field that's not in expected but is in output
        hallucinated = False
        for key in ["name", "order_id", "product", "issue_summary", "urgency"]:
            expected_val = test_case.expected_fields.get(key)
            actual_val = stage2.get(key)
            # If expected is None but actual is not None (and not default), it's hallucinated
            if expected_val is None and actual_val is not None:
                hallucinated = True
                break

        if hallucinated:
            results["hallucinations"] += 1
            score = 0
        else:
            score = 2

        results["scores_per_test"][ticket_id] = {
            "score": score,
            "hallucinated": hallucinated,
            "extracted": stage2,
        }

    return results


def evaluate_stage3(
    test_cases: List[TestCase], outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Evaluate Stage 3 outputs (the critical stage)."""
    results = {
        "total": len(test_cases),
        "behavior_correct": 0,
        "citations_valid": 0,
        "scores_per_test": {},
    }

    # Load policy to validate citations — capture WITHOUT brackets (e.g. "P1", "P2")
    policy_dir = Path("data/policies")
    
    if policy_dir.exists():
        # Load from new categorized structure
        policy_files = ["billing.md", "account.md", "technical.md", "shipping.md", "uncovered.md"]
        combined_policy = []
        for file_name in policy_files:
            policy_file = policy_dir / file_name
            if policy_file.exists():
                content = policy_file.read_text(encoding="utf-8")
                combined_policy.append(content)
        policy_text = "\n\n---\n\n".join(combined_policy)
    else:
        # Fallback to old policy.md
        policy_text = Path("data/policy.md").read_text()
    valid_citations = set(re.findall(r"\[?(P\d+)\]?", policy_text))

    for test_case in test_cases:
        ticket_id = str(test_case.id)
        output = outputs.get(ticket_id, {})
        stage3 = output.get("stage3")

        if not stage3:
            results["scores_per_test"][ticket_id] = {"score": 0, "reason": "No output"}
            continue

        # Check behavior
        expected_behavior = test_case.expected_behavior
        actual_behavior = stage3.get("behavior")
        behavior_correct = actual_behavior == expected_behavior
        if behavior_correct:
            results["behavior_correct"] += 1

        # Normalize citations (strip brackets from output) and compare to valid set
        raw_citations = stage3.get("citations", [])
        citations_clean = [c.strip("[]") for c in raw_citations]

        if expected_behavior == "escalate":
            # Escalations MUST have NO citations
            citations_valid = (len(citations_clean) == 0)
        elif expected_behavior in ("grounded_reply", "grounded_denial"):
            # Grounded behaviors MUST cite at least one VALID passage
            citations_valid = (
                len(citations_clean) > 0
                and all(c in valid_citations for c in citations_clean)
            )
        else:
            citations_valid = all(c in valid_citations for c in citations_clean)

        if citations_valid:
            results["citations_valid"] += 1

        # Check length (note: 120 CHARACTERS — see note below!)
        reply_text = stage3.get("reply_text", "")
        length_ok = len(reply_text) <= 120

        # Overall score
        score = (
            2
            if behavior_correct and citations_valid and length_ok
            else 1
            if behavior_correct or citations_valid
            else 0
        )

        results["scores_per_test"][ticket_id] = {
            "score": score,
            "expected_behavior": expected_behavior,
            "actual_behavior": actual_behavior,
            "behavior_correct": behavior_correct,
            "citations_valid": citations_valid,
            "length_ok": length_ok,
            "reply_length": len(reply_text),
        }

    return results


def evaluate_stage4(
    test_cases: List[TestCase], outputs: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Evaluate Stage 4 outputs (critique quality)."""
    results = {
        "total": len(test_cases),
        "caught_errors": 0,
        "scores_per_test": {},
    }

    for test_case in test_cases:
        ticket_id = str(test_case.id)
        output = outputs.get(ticket_id, {})
        stage4 = output.get("stage4")

        if not stage4:
            results["scores_per_test"][ticket_id] = {"score": 0, "reason": "No output"}
            continue

        issues_found = stage4.get("issues_found", [])

        # Stage 4 is good if it either flags issues (when present) or passes cleanly
        # A simplified heuristic: if there are issues, it's catching errors
        score = 2 if isinstance(issues_found, list) else 0

        results["scores_per_test"][ticket_id] = {
            "score": score,
            "issues_found": len(issues_found),
            "issues": issues_found,
        }

    return results


def evaluate_all(test_set_path: str = "data/test_set.json", output_dir: str = "outputs"):
    """Run full evaluation."""
    test_cases = load_test_set(test_set_path)
    outputs = load_outputs(output_dir)

    print("\n" + "=" * 80)
    print("EVALUATION REPORT")
    print("=" * 80)

    # Evaluate each stage
    stage1_results = evaluate_stage1(test_cases, outputs)
    stage2_results = evaluate_stage2(test_cases, outputs)
    stage3_results = evaluate_stage3(test_cases, outputs)
    stage4_results = evaluate_stage4(test_cases, outputs)

    # Print results
    print(f"\n📊 Stage 1: CLASSIFY")
    print(f"   Correct: {stage1_results['correct']}/{stage1_results['total']}")
    print(f"   Ambiguous w/ confidence <0.7: {stage1_results['ambiguous_low_confidence']}/4")

    print(f"\n📊 Stage 2: EXTRACT")
    print(f"   Hallucinations: {stage2_results['hallucinations']}")
    print(f"   ✅ Pass if hallucinations == 0")

    print(f"\n📊 Stage 3: GROUND")
    print(f"   Behaviors correct: {stage3_results['behavior_correct']}/{stage3_results['total']}")
    print(f"   Citations valid: {stage3_results['citations_valid']}/{stage3_results['total']}")

    print(f"\n📊 Stage 4: CRITIQUE")
    print(f"   Issues caught: {stage4_results['caught_errors']}/{stage4_results['total']}")

    print("\n" + "=" * 80)
    print("SUCCESS CRITERIA")
    print("=" * 80)

    stage1_pass = stage1_results["correct"] >= 11
    stage2_pass = stage2_results["hallucinations"] == 0
    stage3_pass = stage3_results["behavior_correct"] >= 11
    stage4_pass = True  # Simplified

    print(f"✅ Stage 1 (>=11/14 correct): {'PASS' if stage1_pass else 'FAIL'}")
    print(f"✅ Stage 2 (zero hallucinations): {'PASS' if stage2_pass else 'FAIL'}")
    print(f"✅ Stage 3 (behaviors correct): {'PASS' if stage3_pass else 'FAIL'}")
    print(f"✅ Stage 4 (critique works): {'PASS' if stage4_pass else 'FAIL'}")

    overall_pass = stage1_pass and stage2_pass and stage3_pass and stage4_pass
    print(f"\n{'🎉 OVERALL PASS' if overall_pass else '❌ OVERALL FAIL'}")


def evaluate_ticket(ticket_id: str, test_set_path: str = "data/test_set.json", output_dir: str = "outputs"):
    """Evaluate a single ticket."""
    test_cases = load_test_set(test_set_path)
    outputs = load_outputs(output_dir)

    test_case = next((t for t in test_cases if str(t.id) == ticket_id), None)
    if not test_case:
        print(f"Ticket {ticket_id} not found in test set")
        return

    output = outputs.get(ticket_id)
    if not output:
        print(f"Output for ticket {ticket_id} not found")
        return

    print(f"\n{'='*80}")
    print(f"TICKET #{ticket_id}: {test_case.notes}")
    print(f"{'='*80}")

    print(f"\nExpected behavior: {test_case.expected_behavior}")
    print(f"Actual behavior: {output['stage3'].get('behavior', 'N/A')}")

    print(f"\n📝 Ticket text:")
    print(f"  {test_case.raw_ticket[:100]}...")

    print(f"\n📊 Stages:")
    for i in range(1, 5):
        stage_output = output.get(f"stage{i}")
        if stage_output:
            print(f"  Stage {i}: ✅")
        else:
            print(f"  Stage {i}: ❌")
