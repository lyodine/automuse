"""Utilities that construct scales.
"""

from . import NOTES
from . import Interval
from . import note_i2s
from . import note_s2i


def scale(base_key: str, intervals: list[Interval]) -> list[str]:

    assert isinstance(base_key, str)

    _temp = note_s2i(base_key)
    assert isinstance(_temp, Interval)
    base_key_i: Interval = _temp

    return note_i2s(
        [
            *(_ := (base_key_i) % len(NOTES),),
            *((_ := (_ + each) % len(NOTES)) for each in intervals[:-1]),
        ]
    )
