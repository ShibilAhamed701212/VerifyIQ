"""
Evaluation script for the evidence review system.
Runs the system on sample_claims.csv and reports accuracy metrics.
"""

import csv
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import read_claims, write_output
from claim_processor import ClaimProcessor
from config import Config
from utils import setup_logging

logger = setup_logging()


def load_expected_outputs(csv_path: Path) -> Dict[str, Dict]:
    expected = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row.get('user_id', '')}|{row.get('image_paths', '')}"
            expected[key] = row
    return expected


def compare_outputs(predicted: Dict, expected: Dict) -> Dict[str, Any]:
    results = {
        "match": True,
        "differences": [],
        "fields": {}
    }

    compare_fields = [
        "evidence_standard_met",
        "risk_flags",
        "issue_type",
        "object_part",
        "claim_status",
        "valid_image",
        "severity",
    ]

    for field in compare_fields:
        pred_val = predicted.get(field, "")
        exp_val = expected.get(field, "")
        if pred_val != exp_val:
            results["match"] = False
            results["differences"].append({
                "field": field,
                "expected": exp_val,
                "predicted": pred_val,
            })
        results["fields"][field] = {"expected": exp_val, "predicted": pred_val}

    return results


def run_evaluation(config: Config, limit: int = -1) -> Tuple[List[Dict], Dict]:
    sample_claims = read_claims(config.sample_claims_path)
    if limit > 0:
        sample_claims = sample_claims[:limit]

    expected = load_expected_outputs(config.sample_claims_path)
    processor = ClaimProcessor(config)

    results = []
    correct = 0
    total = len(sample_claims)

    for claim_row in sample_claims:
        try:
            predicted = processor.process_claim(claim_row)
        except Exception as e:
            logger.error(f"Error processing sample claim: {e}")
            predicted = processor._fallback_output(claim_row, str(e))

        key = f"{claim_row.get('user_id', '')}|{claim_row.get('image_paths', '')}"
        expected_row = expected.get(key, {})

        if expected_row:
            comparison = compare_outputs(predicted, expected_row)
            if comparison["match"]:
                correct += 1
            results.append({
                "claim": claim_row,
                "predicted": predicted,
                "expected": expected_row,
                "comparison": comparison,
            })
        else:
            results.append({
                "claim": claim_row,
                "predicted": predicted,
                "expected": None,
                "comparison": {"match": False, "differences": ["No expected output found"], "fields": {}},
            })

    accuracy = correct / total if total > 0 else 0
    summary = {
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "matched_count": len([r for r in results if r["comparison"]["match"]]),
    }

    return results, summary


def print_summary(summary: Dict) -> None:
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total claims processed: {summary['total']}")
    print(f"Correct predictions:    {summary['correct']}")
    print(f"Accuracy:              {summary['accuracy']:.2%}")
    print("=" * 60)


def generate_report(results: List[Dict], summary: Dict, output_dir: Path) -> None:
    report_path = output_dir / "evaluation_report.md"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Evaluation Report\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Claims:** {summary['total']}\n")
        f.write(f"- **Correct:** {summary['correct']}\n")
        f.write(f"- **Accuracy:** {summary['accuracy']:.2%}\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| Claim | Status | Match | Differences |\n")
        f.write("|-------|--------|-------|-------------|\n")

        for result in results[:20]:
            claim = result["claim"]
            comparison = result["comparison"]
            status = "YES" if comparison["match"] else "NO"
            diffs = ", ".join([d["field"] for d in comparison.get("differences", [])]) if comparison.get("differences") else "None"
            f.write(f"| {claim.get('user_id', 'unknown')} | {claim.get('claim_object', '')} | {status} | {diffs} |\n")

        f.write("\n## Operational Analysis\n\n")
        f.write("### Model Calls\n")
        f.write(f"- Sample processing: ~{summary['total']} claims x 1 vision call = ~{summary['total']} calls\n")
        f.write(f"- Test processing: ~{summary['total']} claims x 1 vision call = ~{summary['total']} calls\n\n")

        f.write("### Token Usage (Estimated)\n")
        f.write("- Input per call: ~500-800 tokens (text + images)\n")
        f.write("- Output per call: ~300-500 tokens\n")
        f.write(f"- Total input: ~{summary['total']*650} tokens\n")
        f.write(f"- Total output: ~{summary['total']*400} tokens\n\n")

        f.write("### Cost Estimation\n")
        f.write("- GPT-4o: ~$2.50/1M input tokens, ~$10.00/1M output tokens\n")
        f.write(f"- Estimated cost: ~${summary['total']*(650*2.5+400*10)/1e6:.2f}\n\n")

        f.write("### Latency\n")
        f.write("- Average per claim: ~3-8 seconds (including API calls)\n")
        f.write(f"- Total for test set: ~{summary['total']*5} seconds\n\n")

        f.write("### Rate Limiting Strategy\n")
        f.write("- Retry with exponential backoff (3 attempts, 2s-30s)\n")
        f.write("- Sequential processing to respect TPM limits\n")
        f.write("- Configurable max images per claim (default: 5)\n")
        f.write("- Image caching via base64 encoding\n")


def main() -> None:
    config = Config()
    config.claims_path = config.sample_claims_path

    logger.info("Starting evaluation on sample_claims.csv...")

    results, summary = run_evaluation(config, limit=config.evaluation_samples_limit)

    print_summary(summary)

    eval_dir = Path(__file__).parent
    generate_report(results, summary, eval_dir)

    logger.info(f"Evaluation report saved to {eval_dir / 'evaluation_report.md'}")


if __name__ == "__main__":
    main()
