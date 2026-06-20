"""VerifyIQ — Multi-Modal Claim Verification Platform.

VerifyIQ processes images and claim text to determine whether damage claims
are supported, contradicted, or need more evidence. It combines deterministic
rule engines with multi-modal VLM analysis for accurate, explainable decisions.
"""

from importlib.metadata import PackageNotFoundError, version as _version

try:
    __version__ = _version("verifyiq")
except PackageNotFoundError:
    __version__ = "0.1.0-dev"
