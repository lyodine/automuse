"""Patterns that are useful for constructing
scales and chords.

A scale is constructed with a note and one such pattern
(for example, C major consists of the note C as well as
the 2\\ :sup:`nd`, 4\\ :sup:`th`, 5\\ :sup:`th` ... and so on,
notes from C.) This pattern is the mode (or key) of the scale.

Whereas scales (see :mod:`scale`) are constructed by picking notes in a music
space, chords are (see :mod:`chord`) constructed by picking notes from a scale.
Both (:mod:`scale`) and (:mod:`chord`) can use constants defined
in this module.
"""

from typing import Sequence
from . import Interval, Offset


# Construct modes of the major scale.
# Default shift to right
def _circular_shift(intervals: list[Interval],
                    shift_by: int) -> list[Interval]:
    """Shift :arg:`seq` to the right by
    :arg:`shift_by` as if it were a cyclic buffer.
    """
    return intervals[-shift_by:] + intervals[:-shift_by]


def reduce_mode(mode: list[Interval],
                indices: list[int]) -> list[Interval]:
    """Reduce :arg:`mode` to only include notes at :arg:`indices`.

    For example, :code:`scale("C", MAJOR)` returns
    :code:`["C", "D", ..., "B"]`;
    :code:`scale("C", reduce_mode(MAJOR, [0, 2, 4])` returns
    only :code:`["C", "E", "G"]`.
    """

    mode_as_offsets: list[Offset] = intervals_to_offsets(mode)

    offsets_to_use: list[Offset] = [mode_as_offsets[i]
                                    for i in sorted(indices)]

    return offsets_to_intervals(offsets_to_use)


def pentatonic_major(hep: list[Interval]) -> list[Interval]:
    assert len(hep) == 6
    return reduce_mode(hep, [x - 1 for x in [1, 2, 3, 5, 6]])


def pentatonic_minor(hep: list[Interval]) -> list[Interval]:
    assert len(hep) == 6
    return reduce_mode(hep, [x - 1 for x in [1, 3, 4, 5, 7]])


def _add_flat_at(scale: list[Interval], index: int) -> list[Interval]:
    """Add a flat at the :arg:`index`\\ :sup:`th`
    position of :arg:`scale`.

    Note that because indices in this code base
    are 0-based, use :code:`index=n-1` to add a
    flat of the n\\ :sup:`th` note.

    Actually I'm not sure if this is how things work.
    Trial and error be your friend, or something.
    """
    index = index - 1

    return scale[:index] \
        + [scale[index] - 1, 1] \
        + scale[index + 1:]


def blues_major(hep: list[Interval]) -> list[Interval]:
    # Maybe it is correct? The warning message is annoying
    #   though, so I removed it.
    # print("Warning: The correctness of"
    #       " `blues_major` has not been verified.")
    return _add_flat_at(pentatonic_major(hep), 2)


def blues_minor(hep: list[Interval]) -> list[Interval]:
    # Maybe it is correct? The warning message is annoying
    #   though, so I removed it.
    # print("Warning: The correctness of"
    #       " blues_minor` has not been verified.")
    return _add_flat_at(pentatonic_minor(hep), 3)


def harmonic_minor(minor_scale: list[Interval]) -> list[Interval]:
    return [*minor_scale[:-1],
            minor_scale[-1] + 1]


def melodic_minor(minor_scale: list[Interval]) -> list[Interval]:
    return [*minor_scale[:-2],
            minor_scale[-2] + 1,
            minor_scale[-1]]


def intervals_to_offsets(intervals: Sequence[Interval]) -> list[Offset]:
    result: list[int] = []
    current_index = 0
    result.append(current_index)
    for _i in intervals:
        current_index += _i
        result.append(current_index)
    return result


def offsets_to_intervals(offsets: Sequence[Offset]) -> list[Interval]:
    if 0 not in offsets:
        raise ValueError("Offsets lack a root (0)."
                         " Cannot convert offsets to intervals.")
    offsets = sorted(offsets)
    _pros = offsets[:-1]
    _epis = offsets[1:]

    result: list[int] = []
    for this_offset, next_offset in zip(_pros, _epis):
        result.append(next_offset - this_offset)
    return result


CHROMATIC: list[Interval] = [1] * 11

WHOLE_TONE: list[Interval] = [2, 2, 2, 2, 2]

MAJOR: list[Interval] = [2, 2, 1, 2, 2, 2]
MINOR: list[Interval] = [2, 1, 2, 2, 1, 2]

M = MAJOR
m = MINOR

MINOR_NATURAL = MINOR
MINOR_HARMONIC: list[Interval] = [2, 1, 2, 2, 1, 3]

MINOR_MELODIC: list[Interval] = [2, 1, 2, 2, 2, 2]

_MAJOR_7 = MAJOR + [1]
IONIAN: list[Interval] = _circular_shift(_MAJOR_7, 0)[:-1]
DORIAN: list[Interval] = _circular_shift(_MAJOR_7, -1)[:-1]
PHRYGIAN: list[Interval] = _circular_shift(_MAJOR_7, -2)[:-1]
LYDIAN: list[Interval] = _circular_shift(_MAJOR_7, -3)[:-1]
MIXOLYDIAN: list[Interval] = _circular_shift(_MAJOR_7, -4)[:-1]
AEOLIAN: list[Interval] = _circular_shift(_MAJOR_7, -5)[:-1]
LOCRIAN: list[Interval] = _circular_shift(_MAJOR_7, -6)[:-1]


DIMINISHED_WHOLE_HALF: list[Interval] = [2, 1, 2, 1, 2, 1, 2]
DIMINISHED_HALF_WHOLE: list[Interval] = [1, 2, 1, 2, 1, 2, 1]
AUGMENTED: list[Interval] = [3, 1, 3, 1, 3]

MAJOR_PENTATONIC = pentatonic_major(MAJOR)
MINOR_PENTATONIC = pentatonic_minor(MINOR)

MAJOR_BLUES = blues_major(MAJOR)
MINOR_BLUES = blues_minor(MINOR)

TRIAD_MAJOR = [4, 3]  # Δ7
TRIAD_MINOR = [3, 4]  # Δ7
SEVENTH_MAJOR = [4, 3, 4]  # Δ7
SEVENTH_MINOR = [3, 4, 4]  # m7
SEVENTH_DOMINANT = [4, 3, 3]  # 7
SEVENTH_DIMINISHED = [3, 3, 3]  # o7
SEVENTH_MINOR_MAJOR = [3, 4, 4]  # mM7
SEVENTH_HALF_DIMINISHED = [3, 3, 4]  # ø7
SEVENTH_AUGMENTED_MAJOR = [4, 4, 3]  # +Δ7
SEVENTH_AUGMENTED = [4, 4, 2]  # +7
SEVENTH_DIMINISHED_MAJOR = [3, 3, 5]  # oM
