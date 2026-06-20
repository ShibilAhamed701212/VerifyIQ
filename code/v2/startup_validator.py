"""Startup validation — fail fast on missing configuration or resources."""

import importlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


class StartupValidator:
    """Validates environment configuration on startup."""

    REQUIRED_API_KEYS = ["GEMINI_API_KEY", "OPENROUTER_API_KEY"]
    REQUIRED_DIRECTORIES = [
        "dataset/images/test",
        "dataset/images/sample",
    ]
    REQUIRED_PACKAGES = ["pytesseract", "PIL", "google.genai"]

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def validate_api_keys(self) -> dict:
        """Check required API keys are set and non-empty."""
        missing = []
        for key in self.REQUIRED_API_KEYS:
            value = os.environ.get(key)
            if not value:
                missing.append(key)
        if missing:
            return {
                "check": "api_keys",
                "status": "fail",
                "detail": f"Missing environment variables: {', '.join(missing)}",
            }
        return {
            "check": "api_keys",
            "status": "pass",
            "detail": "All required API keys are set",
        }

    def validate_directories(self) -> dict:
        """Check required data directories exist."""
        missing = []
        for d in self.REQUIRED_DIRECTORIES:
            path = self.base_path / d
            if not path.is_dir():
                missing.append(str(path))
        if missing:
            return {
                "check": "directories",
                "status": "fail",
                "detail": f"Missing directories: {', '.join(missing)}",
            }
        return {
            "check": "directories",
            "status": "pass",
            "detail": "All required directories exist",
        }

    def validate_dependencies(self) -> dict:
        """Check required Python packages are importable."""
        failed = []
        for pkg in self.REQUIRED_PACKAGES:
            try:
                importlib.import_module(pkg)
            except ImportError:
                failed.append(pkg)
        if failed:
            return {
                "check": "dependencies",
                "status": "fail",
                "detail": f"Missing packages: {', '.join(failed)}",
            }
        return {
            "check": "dependencies",
            "status": "pass",
            "detail": "All required packages are importable",
        }

    def validate_vision_availability(self) -> dict:
        """Check if vision providers are reachable."""
        try:
            from code.v2.pipeline import V2Pipeline
            from code.v2.vision_manager import VisionState
            pipeline = V2Pipeline()
            state = pipeline.vision_manager.state
            mode = pipeline.vision_manager.mode.value
            report = pipeline.vision_manager.get_health_report()
            best = report.get("best_provider")

            if state == VisionState.UNAVAILABLE and mode == "production":
                return {
                    "check": "vision_availability",
                    "status": "fail",
                    "detail": (
                        "No vision provider available. Set VERIFYIQ_MODE=demo or "
                        "VERIFYIQ_MODE=research to run without VLM. "
                        f"Provider status: {report['providers']}"
                    ),
                }
            if state == VisionState.UNAVAILABLE:
                return {
                    "check": "vision_availability",
                    "status": "warn",
                    "detail": (
                        f"No vision provider available. Running in {mode} mode — "
                        "image analysis disabled."
                    ),
                }
            if state == VisionState.DEGRADED:
                return {
                    "check": "vision_availability",
                    "status": "warn",
                    "detail": f"Vision degraded — primary provider unavailable, using {best}.",
                }
            return {
                "check": "vision_availability",
                "status": "pass",
                "detail": f"Vision available via {best}.",
            }
        except Exception as exc:
            return {
                "check": "vision_availability",
                "status": "fail",
                "detail": f"Vision check error: {exc}",
            }

    def validate_all(self) -> dict:
        """Run all checks and return aggregated result."""
        checks = [
            self.validate_api_keys(),
            self.validate_directories(),
            self.validate_dependencies(),
            self.validate_vision_availability(),
        ]
        statuses = [c["status"] for c in checks]
        if "fail" in statuses:
            overall_status = "unhealthy"
            failed_count = sum(1 for s in statuses if s == "fail")
            summary = f"{failed_count} check(s) failed"
        elif "warn" in statuses:
            overall_status = "degraded"
            summary = "Degraded — some checks have warnings"
        else:
            overall_status = "healthy"
            summary = "All systems nominal"

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": overall_status,
            "checks": checks,
            "summary": summary,
        }

    def write_health_report(self, path: str) -> None:
        """Write JSON health report to given path."""
        report = self.validate_all()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
