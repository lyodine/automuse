"""Utilities that construct scales.
"""

from . import NOTES
from . import Interval
from . import note_i2s
from . import note_s2i
from .modes import offsets_to_intervals


def scale(tonic: str,
          mode: list[Interval],
          include_tonic: bool = True,
          use_offsets: bool = False) -> list[str]:
    """Construct a scale in :arg:`mode` from
    :arg:`tonic`.

    Args:
        tonic: A note like :code:`C#` and :code:`C#4`.
        mode: A sequence of intervals, like
            :code:`[2, 2, 1, 2, 2, 2]` for the major scale. See
            :mod:`.modes` for pre-made options.
        include_tonic: If :code:`True`, then prepend :code:`tonic`
            to the result.
        use_offsets: If :code:`True`, the interpret :arg:`mode`
            as a sequence of :class:`.Offset`\\ s
            (instead of :class:`.Interval`\\ s). Note that 
    """
    if use_offsets:
        mode = offsets_to_intervals(mode)
    return note_i2s(
        [
            *(_ := (note_s2i(tonic)) % len(NOTES),
              [_] if include_tonic else [])[1],
            *((_ := (_ + each) % len(NOTES)) for each in mode[:]),
        ]
    )
