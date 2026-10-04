from pathlib import Path

import pytest

from vtc.script import ScriptError, load_script

EXAMPLES = Path(__file__).parent.parent / "examples"


def test_loads_example():
    script = load_script(EXAMPLES / "nvidia.script.yaml")
    assert len(script.segments) == 3
    assert script.segments[2].chart is None

    first = script.segments[0].chart
    assert (first.ticker, first.start_year, first.end_year) == ("NVDA", 2023, 2025)
    assert script.style.fps == 30


def write_script(tmp_path, chart_block: str) -> Path:
    """Make a one-segment script in a temp folder, next to a copy of the style file."""
    (tmp_path / "channel-dark.yaml").write_text((EXAMPLES / "channel-dark.yaml").read_text())
    path = tmp_path / "bad.script.yaml"
    path.write_text(
        "style: channel-dark.yaml\n"
        "segments:\n"
        '  - line: "Some line."\n'
        f"    chart: {chart_block}\n"
    )
    return path


@pytest.mark.parametrize(
    "chart_block, expected",
    [
        ("{type: pie, ticker: NVDA, metric: revenue, range: 2023-2025}", "unknown chart type"),
        ("{type: line, metric: revenue, range: 2023-2025}", "missing 'ticker'"),
        ("{type: line, ticker: NVDA, metric: revenue, range: 2025-2023}", "runs backwards"),
        ("{type: line, ticker: NVDA, metric: revenue, range: 2023}", "must look like"),
        ("{type: line, ticker: NVDA, metric: profit, range: 2023-2025}", "unknown metric"),
    ],
)
def test_bad_chart_fails_loudly(tmp_path, chart_block, expected):
    with pytest.raises(ScriptError, match=expected):
        load_script(write_script(tmp_path, chart_block))


def test_missing_style_file(tmp_path):
    path = tmp_path / "s.yaml"
    path.write_text('style: nope.yaml\nsegments:\n  - line: "Hi."\n')
    with pytest.raises(ScriptError, match="file not found"):
        load_script(path)