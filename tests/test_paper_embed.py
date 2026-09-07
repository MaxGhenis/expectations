"""Lockstep tests for the /paper/ embedded view (the paper-embed pattern)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WRAPPER = ROOT / "site" / "paper" / "index.html"
WEB = ROOT / "site" / "paper" / "web"


def test_wrapper_and_render_exist():
    assert WRAPPER.exists()
    assert (WEB / "index.html").exists()
    assert (WEB / "index.pdf").exists()


def test_version_param_lockstep():
    html = WRAPPER.read_text()
    versions = set(re.findall(r"web/index\.(?:html|pdf)\?v=([\w-]+)", html))
    assert len(versions) == 1, f"version params out of lockstep: {versions}"
    # Every web/ link carries the version param.
    unversioned = re.findall(r"web/index\.(?:html|pdf)(?!\?v=)", html)
    assert not unversioned, "unversioned link to the raw render"


def test_iframe_hardening():
    html = WRAPPER.read_text()
    iframe = re.search(r"<iframe[^>]+>", html, re.DOTALL).group(0)
    assert (
        'sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox"'
        in iframe
    )
    assert 'referrerpolicy="same-origin"' in iframe
    assert 'loading="lazy"' in iframe
    assert "title=" in iframe


def test_manuscript_numbers_are_computed():
    """The render must carry values computed from outputs/ (no drift):
    the abstract's row count appears only if the setup chunk executed."""
    render = (WEB / "index.html").read_text()
    assert "3,695" in render or "3,687" in render


def test_equations_render_without_iframe_scripts():
    """The sandbox blocks MathJax; equations must already contain native math."""
    render = (WEB / "index.html").read_text()
    assert '<math display="block"' in render
    assert 'xmlns="http://www.w3.org/1998/Math/MathML"' in render
    assert '<span class="math display">\\[' not in render
