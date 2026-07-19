"""bio-run-crate: validate biological analysis-run metadata and build RO-Crates."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("bio-run-crate")
except PackageNotFoundError:  # pragma: no cover - only when running uninstalled
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
