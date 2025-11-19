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

from collections import deque

from omusic import reach
from typing import Sequence
from . import Interval


# Construct modes of the major scale.
# Default shift to right
def _circular_shift(intervals: list[Interval],
                    shift_by: int) -> list[Interval]:
    """Shift :arg:`seq` to the right by
    :arg:`shift_by` as if it were a cyclic buffer.
    """
    return intervals[-shift_by:] + intervals[:-shift_by]


def _reduce_interval(intervals: list[Interval],
                     indices: list[int]) -> list[Interval]:

    indices = [x - 1 for x in indices][1:]
    assert len(indices) < len(intervals)

    accumulator: int = 0
    adjudicator: list[Interval] = []

    indices = sorted(indices)
    indices_poppable: deque[int] = deque(indices)

    for i in range(len(intervals)):
        if not indices_poppable:
            adjudicator.append(accumulator)
            break
        accumulator += intervals[i]
        if indices_poppable[0] == i:
            adjudicator.append(accumulator)
            accumulator = 0
            indices_poppable.popleft()

    return adjudicator


def _pentatonic_major(hep: list[Interval]) -> list[Interval]:
    assert len(hep) == 7

    return _reduce_interval(hep, [x - 1 for x in [1, 2, 3, 5, 6]])


def _pentatonic_minor(hep: list[Interval]) -> list[Interval]:
    assert len(hep) == 7

    return _reduce_interval(hep, [x - 1 for x in [1, 3, 4, 5, 7]])


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


def _blues_major(hep: list[Interval]) -> list[Interval]:
    # Maybe it is correct? The warning message is annoying
    #   though, so I removed it.
    # print("Warning: The correctness of"
    #       " `blues_major` has not been verified.")
    return _add_flat_at(_pentatonic_major(hep), 2)


def _blues_minor(hep: list[Interval]) -> list[Interval]:
    # Maybe it is correct? The warning message is annoying
    #   though, so I removed it.
    # print("Warning: The correctness of"
    #       " blues_minor` has not been verified.")
    return _add_flat_at(_pentatonic_minor(hep), 3)


def _harmonic_minor(minor_scale: list[Interval]) -> list[Interval]:
    return [*minor_scale[:-2],
            minor_scale[-2] + 1,
            *minor_scale[-1:]]


def _melodic_minor(minor_scale: list[Interval]) -> list[Interval]:
    return [*minor_scale[:-3],
            minor_scale[-3] + 1,
            *minor_scale[-2:]]


def _count_triad(root: str,
                 interval_list: Sequence[str]) -> list[str]:
    global interval
    return [reach(root, interval)
            for interval in interval_list]


def _count_triad_major(root: str) -> list[str]:
    return _count_triad(root, ["perfect 8", "major 3", "perfect 5"])


def _count_triad_minor(root: str) -> list[str]:
    return _count_triad(root, ["perfect 8", "minor 3", "perfect 5"])


def _count_triad_augmented(root: str) -> list[str]:
    return _count_triad(root, ["perfect 8", "major 3", "augmented 5"])


def _count_triad_diminished(root: str) -> list[str]:
    return _count_triad(root, ["perfect 8", "minor 3", "diminished 5"])


MAJOR: list[Interval] = [2, 2, 1, 2, 2, 2, 1]
MINOR: list[Interval] = [2, 1, 2, 2, 1, 2, 2]

MINOR_NATURAL = MINOR
MINOR_HARMONIC: list[Interval] = [2, 1, 2, 2, 1, 3, 1]

MINOR_MELODIC: list[Interval] = [2, 1, 2, 2, 2, 2, 2]

IONIAN: list[Interval] = _circular_shift(MAJOR, 0)
DORIAN: list[Interval] = _circular_shift(MAJOR, -1)
PHRYGIAN: list[Interval] = _circular_shift(MAJOR, -2)
LYDIAN: list[Interval] = _circular_shift(MAJOR, -3)
MIXOLYDIAN: list[Interval] = _circular_shift(MAJOR, -4)
AEOLIAN: list[Interval] = _circular_shift(MAJOR, -5)
LOCRIAN: list[Interval] = _circular_shift(MAJOR, -6)


DIMINISHED_WHOLE_HALF: list[Interval] = [2, 1] * 4
DIMINISHED_HALF_WHOLE: list[Interval] = [1, 2] * 4
AUGMENTED: list[Interval] = [3, 1, 3, 1, 3, 1]

MAJOR_PENTATONIC = _pentatonic_major(MAJOR)
MINOR_PENTATONIC = _pentatonic_minor(MINOR)

MAJOR_BLUES = _blues_major(MAJOR)
MINOR_BLUES = _blues_minor(MINOR)
