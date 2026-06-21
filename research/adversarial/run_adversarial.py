"""Run VerifyIQ on adversarial claims and produce report data."""

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from claim_processor import ClaimProcessor
from config import Config
from utils import setup_logging
from main import read_claims

logger = setup_logging()


def run_on_claims(claims_path: Path, output_dir: Path):
    config = Config()
    config.claims_path = claims_path
    processor = ClaimProcessor(config)

    claims = read_claims(claims_path)
    results = []
    
    for i, claim_row in enumerate(claims):
        user_id = claim_row.get("user_id", f"claim_{i}")
        try:
            result = processor.process_claim(claim_row)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed on {user_id}: {e}")
            results.append({
                "user_id": user_id,
                "claim_status": "not_enough_information",
                "risk_flags": "manual_review_required",
                "evidence_standard_met": "false",
                "issue_type": "unknown",
                "object_part": "unknown",
                "valid_image": "false",
                "severity": "unknown",
                "error": str(e),
            })

    # Save results
    output_path = output_dir / "adversarial_results.csv"
    fieldnames = [
        "user_id", "image_paths", "user_claim", "claim_object",
        "evidence_standard_met", "evidence_standard_met_reason",
        "risk_flags", "issue_type", "object_part", "claim_status",
        "claim_status_justification", "supporting_image_ids",
        "valid_image", "severity",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            cleaned = {field: row.get(field, "") for field in fieldnames}
            writer.writerow(cleaned)

    # Save summary
    summary = {
        "total": len(claims),
        "processed": len(results),
        "status_counts": {},
        "issue_type_counts": {},
        "risk_flag_counts": {},
        "severity_counts": {},
    }
    for r in results:
        status = r.get("claim_status", "unknown")
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        issue = r.get("issue_type", "unknown")
        summary["issue_type_counts"][issue] = summary["issue_type_counts"].get(issue, 0) + 1
        sev = r.get("severity", "unknown")
        summary["severity_counts"][sev] = summary["severity_counts"].get(sev, 0) + 1
        flags = r.get("risk_flags", "none")
        for flag in flags.split(";"):
            flag = flag.strip()
            if flag and flag != "none":
                summary["risk_flag_counts"][flag] = summary["risk_flag_counts"].get(flag, 0) + 1

    summary_path = output_dir / "adversarial_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to {output_path}")
    print(f"Summary saved to {summary_path}")
    print(json.dumps(summary, indent=2))

    return results


if __name__ == "__main__":
    claims_path = Path(__file__).parent / "adversarial_claims.csv"
    output_dir = Path(__file__).parent
    run_on_claims(claims_path, output_dir)
