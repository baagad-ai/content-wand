"""Shared test setup. Every test runs against a throwaway state directory."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "content-wand"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))


class IsolatedState(unittest.TestCase):
    """Gives each test its own CONTENT_WAND_HOME and working directory."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.home = self.root / "home"
        self.cwd = self.root / "project"
        self.cwd.mkdir()
        self._saved_env = {k: os.environ.get(k) for k in ("CONTENT_WAND_HOME", "CONTENT_WAND_UPDATES", "CONTENT_WAND_DEV")}
        os.environ["CONTENT_WAND_HOME"] = str(self.home)
        os.environ.pop("CONTENT_WAND_UPDATES", None)
        os.environ.pop("CONTENT_WAND_DEV", None)
        self._saved_cwd = os.getcwd()
        os.chdir(self.cwd)
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        os.chdir(self._saved_cwd)
        for k, v in self._saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
