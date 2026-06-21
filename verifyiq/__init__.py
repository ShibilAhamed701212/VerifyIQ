"""VerifyIQ — Multi-Modal Claim Verification Platform.

VerifyIQ processes images and claim text to determine whether damage claims
are supported, contradicted, or need more evidence. It combines deterministic
rule engines with multi-modal VLM analysis for accurate, explainable decisions.
"""

import sys as _sys
from pathlib import Path as _Path
from importlib.metadata import PackageNotFoundError, version as _version

# V1 code is frozen at code/ — keep it importable for V2 adapters
_CODE_DIR = str(_Path(__file__).resolve().parent.parent / "code")
if _CODE_DIR not in _sys.path:
    _sys.path.insert(0, _CODE_DIR)

try:
    __version__ = _version("verifyiq")
except PackageNotFoundError:
    __version__ = "0.1.0-dev"
