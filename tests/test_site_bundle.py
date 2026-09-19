"""The static tracker must carry, and correctly describe, what it renders.

These checks are deliberately Node-free: the bundle is parsed as JSON and the
page as text and HTML, so they run in the same CI job as the pipeline tests.
They cover what the browser cannot recover on its own — the concept each round
actually asked about, the pooled median the fan draws, and the claims the notes
make about how the benchmarks were built.
"""

import importlib.util
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUTPUTS = ROOT / "outputs"
DATA_JS = SITE / "data.js"
INDEX_HTML = SITE / "index.html"

CONCEPT_TABLES = ("measures", "calibration", "scores")
SOURCE_CSV = {
    "measures": "measures.csv",
    "calibration": "calibration.csv",
    "scores": "scores.csv",
}


def _gen_data():
    """Import site/gen_data.py by path; ``site`` is a stdlib module name."""
    spec = importlib.util.spec_from_file_location(
        "tracker_gen_data", SITE / "gen_data.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def bundle() -> dict:
    text = DATA_JS.read_text(encoding="utf-8")
    assert text.startswith("const DATA="), "data.js must assign one DATA literal"
    return json.loads(text.removeprefix("const DATA=").rstrip().removesuffix(";"))


@pytest.fixture(scope="module")
def page() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


def _rows(bundle: dict, table: str) -> list[dict]:
    fields = bundle["fields"][table]
    return [dict(zip(fields, row, strict=True)) for row in bundle[table]]


@pytest.mark.parametrize("table", CONCEPT_TABLES)
def test_bundle_carries_concept(bundle, table):
    assert "concept" in bundle["fields"][table]
    rows = _rows(bundle, table)
    assert rows, f"{table} bundle is empty"
    assert all(isinstance(row["concept"], str) and row["concept"] for row in rows)


def test_only_the_measure_bundle_carries_the_pooled_median(bundle):
    assert "q50" in bundle["fields"]["measures"]
    # The fan and the IQR table read q50 from measures; no other table needs it.
    assert all(
        isinstance(row["q50"], (int, float)) for row in _rows(bundle, "measures")
    )


@pytest.mark.parametrize("table", CONCEPT_TABLES)
def test_bundle_concepts_and_pooled_medians_match_the_outputs(bundle, table):
    """Also fails when data.js is stale relative to outputs/.

    The key includes horizon_years because it must: nine early ECB Q1 rounds
    carry both a four- and a five-year longer-term target, so without it two
    rows of one round collapse together and a mis-paired pooled median — which
    the tracker averages into a visible number — would go unnoticed. The
    comparison is a multiset, not a subset test, for the same reason.
    """
    significant = _gen_data().significant
    source = pd.read_csv(OUTPUTS / SOURCE_CSV[table]).dropna(subset=["horizon_class"])

    def key(survey, variable, year, quarter, horizon_class, horizon_years):
        return (
            survey,
            variable,
            int(year),
            int(quarter),
            horizon_class,
            significant(horizon_years),
        )

    expected = Counter(
        (
            key(
                row.survey,
                row.variable,
                row.year,
                row.quarter,
                row.horizon_class,
                row.horizon_years,
            ),
            row.concept,
            significant(row.q50) if table == "measures" else None,
        )
        for row in source.itertuples(index=False)
    )
    actual = Counter(
        (
            key(
                row["survey"],
                row["variable"],
                row["year"],
                row["quarter"],
                row["horizon_class"],
                row["horizon_years"],
            ),
            row["concept"],
            row["q50"] if table == "measures" else None,
        )
        for row in _rows(bundle, table)
    )

    assert actual == expected, (
        f"{table}: bundle and {SOURCE_CSV[table]} differ\n"
        f"  only in bundle: {sorted(actual - expected)[:3]}\n"
        f"  only in csv:    {sorted(expected - actual)[:3]}"
    )


def test_the_duplicate_longer_term_rounds_are_actually_present(bundle):
    """The multiset check above is only meaningful if the duplicates exist."""
    rows = _rows(bundle, "measures")
    duplicated = Counter(
        (
            row["survey"],
            row["variable"],
            row["year"],
            row["quarter"],
            row["horizon_class"],
        )
        for row in rows
    )
    repeated = {key for key, count in duplicated.items() if count > 1}
    assert repeated, "expected early ECB longer-term rounds with two targets"
    assert all(key[4] == "longer_term" for key in repeated), sorted(repeated)[:3]


def test_the_us_concept_changes_survive_into_the_bundle(bundle):
    """The eras the tracker has to name must actually be present to name."""
    rows = _rows(bundle, "measures")
    eras = {(row["variable"], row["concept"]) for row in rows if row["survey"] == "us"}
    assert {"nominal_gnp", "real_gnp", "real_gdp"} == {
        concept for variable, concept in eras if variable == "PRGDP"
    }
    assert {
        "gnp_implicit_deflator",
        "gdp_implicit_deflator",
        "chain_weighted_gdp_price_index",
    } == {concept for variable, concept in eras if variable == "PRPGDP"}


def test_every_bundled_concept_has_a_plain_word_label(page, bundle):
    """An unlabelled concept still renders, via conceptLabel's underscore
    fallback, but as an unreviewed identifier read out as words rather than the
    phrasing chosen for the note ("gnp implicit deflator", not "the GNP implicit
    price deflator"). Every concept the bundle can carry needs a real label."""
    block = re.search(r"const CONCEPT_LABELS = \{(.*?)\n\};", page, re.DOTALL)
    assert block, "site/index.html must define CONCEPT_LABELS"
    labelled = dict(re.findall(r"(\w+): '([^']+)'", block.group(1)))
    bundled = {
        row["concept"] for table in CONCEPT_TABLES for row in _rows(bundle, table)
    }
    assert not bundled - set(labelled), (
        f"unlabelled concepts: {sorted(bundled - set(labelled))}"
    )
    assert not any("_" in label for label in labelled.values())


def test_the_scores_note_does_not_claim_a_real_time_information_set(page):
    """benchmarks.period_completion_ordinal filters on target-period completion,
    and the outcomes are revised. Neither is "information available at the time".
    """
    assert "information available" not in page
    assert "already complete at each forecast round" in page
    assert "revised data" in page


@pytest.mark.parametrize(
    "path", ["README.md", "site/index.html", "site/paper/index.html"]
)
def test_no_shipped_page_or_doc_claims_a_real_time_information_set(path):
    """Fix 3 corrected four files; reverting any one of them re-asserts a
    real-time information set the pipeline does not reconstruct."""
    text = (ROOT / path).read_text(encoding="utf-8")
    assert "information available" not in text
    assert "no-lookahead" not in text


def test_the_fan_draws_the_pooled_median_and_names_the_other_one(page):
    """The centre line and its band must be quantiles of one distribution."""
    fan = page[
        page.index("\nfunction fan() {") : page.index("\nfunction calibration() {")
    ]

    # Drawn geometry: line, y-domain and end label all read pooled q50.
    assert "line(rows.map(row => [roundTime(row), row.q50])" in fan
    assert "line(rows.map(row => [roundTime(row), row.median])" not in fan
    assert "[row.q25, row.q75, row.q50]" in fan
    assert "endpoint(roundTime(last), last.q50" in fan
    assert "last.median" not in fan

    # The respondent-mean median survives only where it is named for what it is.
    assert "'Pooled median'" in fan
    assert "'Median of respondent means'" in fan
    assert "pooled median + pooled q25\u2013q75" in fan
    assert "density-implied means" in fan


class _Attributes(HTMLParser):
    """Collect start-tag attributes for elements the tab pattern depends on."""

    def __init__(self) -> None:
        super().__init__()
        self.tabs: list[dict[str, str]] = []
        self.tablist: dict[str, str] = {}
        self.panel: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("role") == "tab":
            self.tabs.append(attributes)
        elif attributes.get("role") == "tablist":
            self.tablist = attributes
        elif attributes.get("id") == "panel":
            self.panel = attributes


@pytest.fixture(scope="module")
def markup(page) -> _Attributes:
    parser = _Attributes()
    parser.feed(page)
    return parser


def test_tabs_expose_the_full_aria_tab_pattern(markup):
    assert markup.tablist.get("id") == "tabs"
    assert markup.tablist.get("aria-label")
    assert len(markup.tabs) == 6
    for tab in markup.tabs:
        assert tab.get("id"), "each tab needs an id so the panel can be labelled by it"
        assert tab.get("aria-controls") == "panel"
        assert tab.get("data-view")
        assert tab.get("aria-selected") in {"true", "false"}
        assert tab.get("tabindex") in {"0", "-1"}
    selected = [tab for tab in markup.tabs if tab["aria-selected"] == "true"]
    focusable = [tab for tab in markup.tabs if tab["tabindex"] == "0"]
    assert len(selected) == len(focusable) == 1, "roving tabindex: exactly one of each"
    assert selected == focusable, "the focusable tab must be the selected tab"


def test_every_tab_names_a_view_the_page_can_render(markup, page):
    """A typo in data-view makes that tab a silent no-op: setActiveTab returns
    early for a name RENDERERS does not have, so the tab never selects."""
    renderers = re.search(r"const RENDERERS = \{([^}]*)\}", page)
    assert renderers, "site/index.html must define RENDERERS"
    names = {
        entry.split(":")[0].strip()
        for entry in renderers.group(1).split(",")
        if entry.strip()
    }
    assert {tab["data-view"] for tab in markup.tabs} == names
    assert len({tab["id"] for tab in markup.tabs}) == len(markup.tabs), (
        "tab ids must be unique"
    )


def test_the_panel_is_a_tabpanel_named_by_its_tab(markup):
    assert markup.panel.get("role") == "tabpanel"
    selected = next(tab for tab in markup.tabs if tab["aria-selected"] == "true")
    assert markup.panel.get("aria-labelledby") == selected["id"]


def test_a_fragment_cannot_name_an_inherited_property_as_a_view(page):
    """#view=__proto__ once passed a truthiness check and stranded the tab pattern.

    RENDERERS["__proto__"] is Object.prototype, which is truthy, so activeView
    became a name no tab carries: the render threw and every tab was left with
    tabindex="-1", so the tablist could not be reached by keyboard at all.
    """
    assert "Object.hasOwn(RENDERERS, name)" in page
    assert "if (view && isView(view))" in page
    assert "if (!isView(view)) return;" in page
    assert "RENDERERS[view]" not in page, "view lookup must not rest on truthiness"
    # The concept vocabulary is looked up the same way for the same reason.
    assert "Object.hasOwn(CONCEPT_LABELS, id)" in page


def test_tab_keyboard_navigation_and_hash_changes_are_wired(page):
    assert "byId('tabs').addEventListener('keydown'" in page
    # "End" also appears in placeEndpoints and its comment, so a bare substring
    # search over the page cannot tell whether the binding still exists.
    moves = re.search(r"const moves = \{([^}]*)\}", page)
    assert moves, "the keydown handler must map keys to moves"
    for key in ("ArrowRight", "ArrowLeft", "Home", "End"):
        assert f"{key}:" in moves.group(1), f"{key} must be bound in the moves map"
    assert "addEventListener('hashchange'" in page
    # writeHash must stay a replaceState, or the hashchange listener would loop.
    assert "history.replaceState" in page
    assert "history.pushState" not in page
