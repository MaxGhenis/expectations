"""Lockstep tests for the embedded manuscript views (the paper-embed pattern).

The site serves two manuscripts: the panorama paper at ``/paper/`` and the
growth companion's paper at ``/growth/paper/``. Each has a hand-written
wrapper framing its own versioned render, so every check runs against both.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

#: Wrapper directory, and a computed value the render only carries if that
#: manuscript's setup chunk executed against ``outputs/``.
EMBEDS = {
    "panorama": (ROOT / "site" / "paper", ("3,695", "3,687")),
    "growth": (ROOT / "site" / "growth" / "paper", ("3,695", "3,687")),
}


@pytest.fixture(params=sorted(EMBEDS), ids=sorted(EMBEDS))
def embed(request):
    directory, computed = EMBEDS[request.param]
    return directory / "index.html", directory / "web", computed


def test_wrapper_and_render_exist(embed):
    wrapper, web, _ = embed
    assert wrapper.exists()
    assert (web / "index.html").exists()
    assert (web / "index.pdf").exists()


def test_version_param_lockstep(embed):
    wrapper, _, _ = embed
    html = wrapper.read_text()
    versions = set(re.findall(r"web/index\.(?:html|pdf)\?v=([\w-]+)", html))
    assert len(versions) == 1, f"version params out of lockstep: {versions}"
    # Every web/ link carries the version param.
    unversioned = re.findall(r"web/index\.(?:html|pdf)(?!\?v=)", html)
    assert not unversioned, "unversioned link to the raw render"


def test_each_wrapper_frames_its_own_render(embed):
    """A wrapper may only reference its sibling ``web/`` directory."""
    wrapper, _, _ = embed
    html = wrapper.read_text()
    assert "web/index.html" in html
    assert not re.search(r"(?:\.\./|/)[\w/]*web/index\.(?:html|pdf)", html)


def test_iframe_hardening(embed):
    wrapper, _, _ = embed
    html = wrapper.read_text()
    iframe = re.search(r"<iframe[^>]+>", html, re.DOTALL).group(0)
    assert (
        'sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox"'
        in iframe
    )
    assert 'referrerpolicy="same-origin"' in iframe
    assert 'loading="lazy"' in iframe
    assert "title=" in iframe


def test_canonical_url_is_declared(embed):
    """Two manuscripts on one host need one canonical URL each."""
    wrapper, _, _ = embed
    html = wrapper.read_text()
    canonical = re.search(r'<link rel="canonical" href="([^"]+)">', html)
    assert canonical, "wrapper declares no canonical URL"
    assert canonical.group(1).startswith("https://maxghenis.com/expectations/")
    assert f'<meta property="og:url" content="{canonical.group(1)}">' in html


def test_manuscript_numbers_are_computed(embed):
    """The render must carry values computed from outputs/ (no drift):
    the round-target count appears only if the setup chunk executed."""
    _, web, computed = embed
    render = (web / "index.html").read_text()
    assert any(value in render for value in computed)


def test_equations_render_without_iframe_scripts(embed):
    """The sandbox blocks MathJax; equations must already contain native math."""
    _, web, _ = embed
    render = (web / "index.html").read_text()
    assert '<math display="block"' in render
    assert 'xmlns="http://www.w3.org/1998/Math/MathML"' in render
    assert '<span class="math display">\\[' not in render
