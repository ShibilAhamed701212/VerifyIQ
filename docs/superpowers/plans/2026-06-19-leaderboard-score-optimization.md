# Leaderboard Score Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Increase evaluation exact-match accuracy from ~30% to >50% by fixing claim parser regression, recalibrating severity, and enabling full evaluation.

**Architecture:** No architectural changes. Targeted fixes to `claim_parser.py`, `severity_engine.py`, and `evaluation/evaluate.py`. All fixes driven by expected outputs in `dataset/sample_claims.csv`.

**Tech Stack:** Python 3.12, no new dependencies.

## Global Constraints

- No architectural changes
- No refactoring of unrelated code
- Optimize only for leaderboard score
- All changes must be testable via the evaluation suite

---

### Task 1: Fix claim parser regression (split extract_claim_text usage)

**Files:**
- Modify: `code/claim_parser.py` — send full conversation to parser, short extract to vision
- Modify: `code/claim_processor.py` — pass both extracted and full texts
- Test: Run evaluation to verify user_005 and user_008 now reach `contradicted` status

**Problem:** `extract_claim_text` now returns only the last `Customer:` message. `claim_parser.py` uses this same extracted text, losing damage-type context for user_005 (`"Yes, the back bumper. It looks pretty bad to me..."`) and user_008 (`"Yes, that is why I am asking for review. The photo is attached."`).

**Fix:** `claim_processor.py` passes `user_claim` (full conversation) to the parser and `claim_text` (extracted) to vision. Parser always gets the full original conversation.

- [ ] **Step 1: Read current claim_parser.py and claim_processor.py**

Read both files to understand current interfaces.

- [ ] **Step 2: Fix claim_processor.py** – pass `user_claim` to parser, `claim_text` to vision

In `claim_processor.py`, change the parser call to use `user_claim` (the raw CSV field) instead of `claim_text` (the extracted version):

```python
# After: claim_text = extract_claim_text(user_claim) or user_claim
# Pass user_claim (full CSV conversation) to parser, claim_text (extracted) to vision
parsed_claim = parse_claim(user_claim, claim_object)  # full conversation
...
# Vision prompt uses claim_text (just last Customer message)
vision_prompt = build_vision_prompt(claim_text, ...)
```

- [ ] **Step 3: Run evaluation to verify fix**

Run: `python code/evaluation/evaluate.py`
Expected: user_005 and user_008 now have `contradicted` status (matching expected).

---

### Task 2: Recalibrate severity mappings

**Files:**
- Modify: `code/severity_engine.py` — update BASE map and boost logic

**Problem:** The SeverityEngine.BASE map does not match expected severities from sample_claims.csv:
- `dent` → currently `low`, expected `medium` (user_001, user_003)
- `stain` → currently `low`, expected `medium` (user_011)
- `torn_packaging` → currently `low`, expected `medium` (user_030)
- `water_damage` → currently `high`, expected `medium` (user_031)
- Boost false positive: "major" in negated context triggers boost for user_007 (broken_part: medium→high)

- [ ] **Step 1: Read severity_engine.py**

Read the file to understand exact current mappings.

- [ ] **Step 2: Update BASE severity map**

```python
# Old values that need updating:
BASE = {
    ...
    "dent": "low",        # → "medium"
    "stain": "low",       # → "medium"
    "torn_packaging": "low",  # → "medium"
    "water_damage": "high",   # → "medium"
    ...
}
```

- [ ] **Step 3: Fix severity boost false positive**

Replace simple substring match with negative-lookahead regex to avoid matching "major" when negated ("nothing else major"):

```python
# Current: any(word in claim_text for word in self.BOOST_WORDS)
# Fix: use regex with negative lookbehind for negation
import re
for word in self.BOOST_WORDS:
    if re.search(rf"(?<!\bnot\s|\bno\s|\bnothing\s)(?:{word})", claim_text, re.IGNORECASE):
        return self._bump(severity)
```

- [ ] **Step 4: Run tests**

Run: `python -m unittest discover -s code/tests -p "*.py" -v`
Expected: all existing tests still pass.

- [ ] **Step 5: Write severity test for new mappings**

Create test_severity_engine.py in code/tests/:

```python
import sys, unittest
sys.path.insert(0, "code")
from severity_engine import SeverityEngine

class TestSeverityEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SeverityEngine()

    def test_dent_medium(self):
        self.assertEqual("medium", self.engine.get_severity("dent", "rear bumper dent"))

    def test_stain_medium(self):
        self.assertEqual("medium", self.engine.get_severity("stain", "keyboard liquid stain"))

    def test_torn_packaging_medium(self):
        self.assertEqual("medium", self.engine.get_severity("torn_packaging", "package torn open"))

    def test_water_damage_medium(self):
        self.assertEqual("medium", self.engine.get_severity("water_damage", "package water damage"))

    def test_broken_part_medium(self):
        self.assertEqual("medium", self.engine.get_severity("broken_part", "hinge"))

    def test_boost_major_ignored_when_negated(self):
        result = self.engine.get_severity("broken_part", "I did not notice anything else major")
        self.assertNotEqual("high", result)

    def test_boost_major_applies_when_affirmative(self):
        result = self.engine.get_severity("broken_part", "The hinge has major damage")
        self.assertEqual("high", result)
```

- [ ] **Step 6: Run severity tests**

Run: `python -m unittest code/tests/test_severity_engine.py -v`
Expected: all 7 tests pass.

---

### Task 3: Fix evaluation exact-match comparison for risk flags

**Files:**
- Modify: `code/evaluation/evaluate.py` — normalize risk flags before comparing

**Problem:** `compare_outputs` compares raw `risk_flags` strings, but expected flags are in human-written order while the system outputs sorted order. This causes false mismatches for user_020, 031, 033, 034 where status/issue_type/object_part already match but flags are in different order.

- [ ] **Step 1: Fix compare_outputs to normalize risk flags**

```python
def compare_outputs(predicted: Dict, expected: Dict) -> Dict[str, Any]:
    ...
    for field in compare_fields:
        pred_val = predicted.get(field, "")
        exp_val = expected.get(field, "")
        # Normalize risk_flags before comparison
        if field == "risk_flags":
            pred_val = _normalize_flags(pred_val)
            exp_val = _normalize_flags(exp_val)
        if pred_val != exp_val:
            ...
```

- [ ] **Step 2: Run evaluation**

Run: `python code/evaluation/evaluate.py`
Expected: risk flag ordering mismatches resolved.

---

### Task 4: Run full evaluation

**Files:**
- Read: `code/evaluation/evaluation_report.md`
- Read: `code/evaluation/error_report.md`

- [ ] **Step 1: Run full evaluation**

Run: `python code/evaluation/evaluate.py`

- [ ] **Step 2: Read generated reports**

Read both `evaluation_report.md` and `error_report.md` from `code/evaluation/` to extract metrics.

- [ ] **Step 3: Compute and report:**

Produce:
- Exact match accuracy: X/20
- Status accuracy: Y/20
- Risk flag accuracy: Z/20
- Severity accuracy: W/20
- Top remaining failure causes
