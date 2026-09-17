"""Handles extracting a Power Platform solution from a .zip or unpacked folder."""

import os
import shutil
import tempfile
import zipfile
from pathlib import Path


class SolutionExtractor:
    """Context manager that normalises .zip or folder input into a working directory."""

    def __init__(self, input_path: str):
        self.input_path = Path(input_path)
        self._temp_dir: str | None = None
        self.root: Path | None = None

    def __enter__(self) -> "SolutionExtractor":
        if not self.input_path.exists():
            raise FileNotFoundError(f"Solution path not found: {self.input_path}")

        if self.input_path.suffix.lower() == ".zip":
            self._temp_dir = tempfile.mkdtemp(prefix="at_solution_")
            with zipfile.ZipFile(self.input_path) as zf:
                zf.extractall(self._temp_dir)
            self.root = Path(self._temp_dir)
        elif self.input_path.is_dir():
            self.root = self.input_path
        else:
            raise ValueError(
                f"Input must be a .zip file or an unpacked solution folder, got: {self.input_path}"
            )
        return self

    def __exit__(self, *_):
        if self._temp_dir:
            shutil.rmtree(self._temp_dir, ignore_errors=True)

    # ── File helpers ──────────────────────────────────────────────────────────

    def solution_xml(self) -> Path:
        return self.root / "solution.xml"

    def customizations_xml(self) -> Path:
        return self.root / "customizations.xml"

    def canvas_apps_dir(self) -> Path:
        return self.root / "CanvasApps"

    def workflows_dir(self) -> Path:
        return self.root / "Workflows"

    def has_customizations(self) -> bool:
        return self.customizations_xml().exists()

    def find_files(self, glob_pattern: str) -> list[Path]:
        return sorted(self.root.glob(glob_pattern))
