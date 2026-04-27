"""ASGI entrypoint that works from both repo root and package directory."""

import sys
from pathlib import Path

try:
	# Standard path when started from the repository root.
	from backend_opriessnig.api import build_app
except ModuleNotFoundError:
	# Fallback when cwd is backend_opriessnig and app is referenced as main:app.
	project_root = Path(__file__).resolve().parent.parent
	sys.path.insert(0, str(project_root))
	from backend_opriessnig.api import build_app


app = build_app()
