import pytest

from vtc.transcribe import fill_missing_times


def word(text, start=None, end=None):
    return {"word": text, "start": start, "end": end}


def times(words):
    return [(w["start"], w["end"]) for w in words]


def test_example_table():
    words = [
        word("so"),
        word("revenue", 0.40, 0.95),
        word("grew", 1.00, 1.30),
        word("40"),
        word("%"),
        word("in", 2.10, 2.25),
        word("2025"),
    ]
    assert times(fill_missing_times(words)) == [
        pytest.approx((0.00, 0.40)),  # start edge, clamped at 0
        pytest.approx((0.40, 0.95)),  # untouched
        pytest.approx((1.00, 1.30)),  # untouched
        pytest.approx((1.30, 1.70)),  # middle, first half of the gap
        pytest.approx((1.70, 2.10)),  # middle, second half of the gap
        pytest.approx((2.10, 2.25)),  # untouched
        pytest.approx((2.25, 2.75)),  # end edge, 0.5 s guess
    ]


def test_two_missing_at_the_start_share_the_guess():
    words = [word("20"), word("25"), word("was", 1.00, 1.20)]
    assert times(fill_missing_times(words))[:2] == [
        pytest.approx((0.50, 0.75)),
        pytest.approx((0.75, 1.00)),
    ]


def test_two_missing_at_the_end_share_the_guess():
    words = [word("in", 1.00, 1.20), word("20"), word("25")]
    assert times(fill_missing_times(words))[1:] == [
        pytest.approx((1.20, 1.45)),
        pytest.approx((1.45, 1.70)),
    ]


def test_missing_first_word_never_goes_below_zero():
    words = [word("2025"), word("was", 0.00, 0.20)]
    assert times(fill_missing_times(words))[0] == pytest.approx((0.00, 0.00))


def test_nothing_missing_is_left_unchanged():
    words = [word("revenue", 0.40, 0.95), word("grew", 1.00, 1.30)]
    assert times(fill_missing_times(words)) == [(0.40, 0.95), (1.00, 1.30)]


def test_every_word_missing_raises():
    with pytest.raises(ValueError):
        fill_missing_times([word("40"), word("%")])