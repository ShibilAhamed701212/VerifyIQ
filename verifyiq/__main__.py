"""VerifyIQ CLI entry point.

Usage:
    verifyiq evaluate    — Run evaluation on sample claims
    verifyiq analyze     — Analyze a single claim
    verifyiq benchmark   — Run benchmarks
    verifyiq version     — Show version
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="verifyiq",
        description="Multi-Modal Claim Verification Platform",
    )
    parser.add_argument(
        "--version", action="store_true", help="Show version and exit"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    sub.add_parser("version", help="Show version")
    eval_cmd = sub.add_parser("evaluate", help="Run evaluation on sample claims")
    eval_cmd.add_argument(
        "--output", "-o", default=None, help="Output path for results"
    )

    sub.add_parser("analyze", help="Analyze a single claim (not yet implemented)")

    args = parser.parse_args()

    if args.version or args.command == "version":
        from verifyiq import __version__
        print(f"verifyiq {__version__}")
        sys.exit(0)

    if args.command == "evaluate":
        _run_evaluate(args)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)


def _run_evaluate(args):
    try:
        import sys as _sys
        from pathlib import Path as _Path
        _code_dir = str(_Path(__file__).resolve().parent.parent / "code")
        if _code_dir not in _sys.path:
            _sys.path.insert(0, _code_dir)

        from code.evaluation.static_evaluate import main as evaluate_main
        from code.config import Config

        config = Config()
        print(f"Running evaluation on {config.sample_claims_path}...")
        evaluate_main()
        print("Evaluation complete.")
    except ImportError as e:
        print(f"Error: evaluation module not available ({e})", file=_sys.stderr)
        _sys.exit(1)
    except Exception as e:
        print(f"Error during evaluation: {e}", file=_sys.stderr)
        _sys.exit(1)


if __name__ == "__main__":
    main()
