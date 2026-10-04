"""Read a script file and its style file, and reject bad input early."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

CHART_TYPES = {"line"}      # v1 draws line charts only
METRICS = {"revenue"}       # v1 fetches revenue only


class ScriptError(ValueError):
    """The script or style file has a mistake in it."""


@dataclass(frozen=True)
class Chart:
    type: str
    ticker: str
    metric: str
    start_year: int
    end_year: int


@dataclass(frozen=True)
class Segment:
    line: str
    chart: Chart | None


@dataclass(frozen=True)
class Style:
    font: str
    font_size: int
    line_color: str
    text_color: str
    grid_color: str
    line_width: float
    fps: int


@dataclass(frozen=True)
class Script:
    style: Style
    segments: list[Segment]


def _read_yaml(path: Path) -> dict:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ScriptError(f"file not found: {path}") from None
    except yaml.YAMLError as e:
        raise ScriptError(f"{path}: not valid YAML: {e}") from None
    if not isinstance(raw, dict):
        raise ScriptError(f"{path}: expected 'key: value' pairs at the top level")
    return raw


def _parse_range(value, where: str) -> tuple[int, int]:
    m = re.fullmatch(r"(\d{4})-(\d{4})", str(value).strip())
    if not m:
        raise ScriptError(f"{where}: range must look like 2023-2025, got {value!r}")
    start, end = int(m.group(1)), int(m.group(2))
    if start > end:
        raise ScriptError(f"{where}: range {value} runs backwards")
    return start, end


def _parse_chart(raw, where: str) -> Chart | None:
    # "chart: none" arrives as the text "none"; a missing key or "chart:" arrives as None
    if raw is None or (isinstance(raw, str) and raw.strip().lower() == "none"):
        return None
    if not isinstance(raw, dict):
        raise ScriptError(f"{where}: chart must be 'none' or a block of settings")

    for key in ("type", "ticker", "metric", "range"):
        if not raw.get(key):
            raise ScriptError(f"{where}: chart is missing '{key}'")

    if raw["type"] not in CHART_TYPES:
        raise ScriptError(
            f"{where}: unknown chart type {raw['type']!r} (allowed: {sorted(CHART_TYPES)})"
        )
    if raw["metric"] not in METRICS:
        raise ScriptError(
            f"{where}: unknown metric {raw['metric']!r} (allowed: {sorted(METRICS)})"
        )

    start, end = _parse_range(raw["range"], where)
    return Chart(
        type=raw["type"],
        ticker=str(raw["ticker"]).upper(),
        metric=raw["metric"],
        start_year=start,
        end_year=end,
    )


def load_style(path: str | Path) -> Style:
    path = Path(path)
    raw = _read_yaml(path)
    try:
        return Style(**raw)
    except TypeError as e:          # a missing or misspelled key
        raise ScriptError(f"{path}: {e}") from None


def load_script(path: str | Path) -> Script:
    path = Path(path)
    raw = _read_yaml(path)

    if not raw.get("style"):
        raise ScriptError(f"{path}: missing 'style'")
    # the style path is written relative to the script file, not to where you run from
    style = load_style(path.parent / raw["style"])

    raw_segments = raw.get("segments")
    if not isinstance(raw_segments, list) or not raw_segments:
        raise ScriptError(f"{path}: 'segments' must be a non-empty list")

    segments = []
    for i, seg in enumerate(raw_segments, start=1):
        where = f"{path.name}, segment {i}"
        if not isinstance(seg, dict):
            raise ScriptError(f"{where}: expected a 'line:' entry")
        line = seg.get("line")
        if not isinstance(line, str) or not line.strip():
            raise ScriptError(f"{where}: missing 'line'")
        segments.append(Segment(line=line.strip(), chart=_parse_chart(seg.get("chart"), where)))

    return Script(style=style, segments=segments)