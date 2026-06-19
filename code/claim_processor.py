"""
Claim processing orchestrator.

Flow:
Vision Analysis -> Evidence Checker -> Rule Engine -> Risk Analyzer ->
Decision Agent -> Output Validator.
"""

import logging
from typing import Any, Dict, Optional

from claim_parser import ClaimParser
from config import Config
from decision_agent import DecisionAgent
from evidence_checker import EvidenceChecker
from output_validator import OutputValidator
from risk_analyzer import RiskAnalyzer
from rule_engine import RuleEngine
from severity_engine import SeverityEngine
from utils import extract_claim_text, parse_image_paths, safe_csv_read
from vision_analyzer import analyze_images

logger = logging.getLogger("evidence_review.processor")


class ClaimProcessor:
    """Runs one claim through the production decision pipeline."""

    def __init__(self, config: Config):
        self.config = config
        self.claim_parser = ClaimParser(config)
        self.evidence_checker = EvidenceChecker(config.evidence_reqs_path)
        self.rule_engine = RuleEngine()
        self.risk_analyzer = RiskAnalyzer(config)
        self.output_validator = OutputValidator(config)
        self.severity_engine = SeverityEngine()
        self.decision_agent = DecisionAgent(self.output_validator, self.severity_engine)
        self.user_history_cache: Dict[str, Dict[str, Any]] = {}
        self._load_user_history()

    def _load_user_history(self) -> None:
        if not self.config.user_history_path.exists():
            logger.warning(f"User history file not found: {self.config.user_history_path}")
            return

        for row in safe_csv_read(self.config.user_history_path):
            user_id = row.get("user_id", "").strip()
            if user_id:
                self.user_history_cache[user_id] = row
        logger.info(f"Loaded history for {len(self.user_history_cache)} users")

    def _get_user_history(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.user_history_cache.get(user_id)

    def process_claim(self, claim_row: Dict[str, str]) -> Dict[str, str]:
        user_id = claim_row.get("user_id", "").strip()
        image_paths_str = claim_row.get("image_paths", "").strip()
        user_claim = claim_row.get("user_claim", "").strip()
        claim_object = claim_row.get("claim_object", "").strip().lower()

        image_paths = parse_image_paths(image_paths_str, self.config.images_dir)
        parser_result = self.claim_parser.parse(user_claim, claim_object)
        user_history = self._get_user_history(user_id)
        claim_text = extract_claim_text(user_claim) or user_claim

        try:
            vision_result = analyze_images(
                image_paths=image_paths,
                user_claim=claim_text,
                claim_object=claim_object,
                config=self.config,
            )

            evidence_result = self.evidence_checker.evaluate(
                claim_object=claim_object,
                parser_result=parser_result,
                vision_result=vision_result,
                total_images=len(image_paths),
            )

            rule_result = self.rule_engine.evaluate(
                parser_result=parser_result,
                vision_result=vision_result,
                evidence_result=evidence_result,
            )

            risk_result = self.risk_analyzer.analyze(
                image_analysis=vision_result,
                user_history=user_history,
                claim_object=claim_object,
                user_claim=user_claim,
                evidence_result=evidence_result,
                rule_result=rule_result,
                image_paths=image_paths,
            )

            return self.decision_agent.build_output_row(
                claim_row=claim_row,
                parser_result=parser_result,
                vision_result=vision_result,
                evidence_result=evidence_result,
                rule_result=rule_result,
                risk_result=risk_result,
            )

        except Exception as e:
            logger.error(f"Processing failed for user {user_id}: {e}", exc_info=True)
            return self.decision_agent.fallback_output(claim_row, str(e))

    def _fallback_output(self, claim_row: Dict[str, str], error_message: str) -> Dict[str, str]:
        return self.decision_agent.fallback_output(claim_row, error_message)
