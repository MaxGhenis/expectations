"""Run the tracker's behavioral checks, which need a JavaScript runtime.

The rest of the suite reads site/index.html as text, which cannot tell whether a
renderer still calls the function it mentions.  tests/page/run.mjs executes the
real page in jsdom and asserts what a reader would see.  CI installs jsdom and
runs it; locally it is skipped unless the dependency is present, so the Python
suite stays usable without a JavaScript toolchain.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "page" / "run.mjs"
JSDOM = ROOT / "node_modules" / "jsdom"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
@pytest.mark.skipif(
    not JSDOM.is_dir(), reason="jsdom is not installed (run: bun install)"
)
def test_the_tracker_page_behaves_as_its_notes_and_labels_claim():
    result = subprocess.run(
        ["node", str(HARNESS)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # A harness that silently ran nothing would also exit 0.
    assert "checks passed" in result.stdout, result.stdout
