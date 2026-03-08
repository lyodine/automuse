"""Utilities that construct chords.
"""
from . import (
    INTERVALS,
    NOTE_NAMES,
    NOTES,
    Interval,
    match_out_numbers,
    note_i2s,
    note_s2i,
    reach,
)

from typing import Literal, Sequence

from .scale import scale


def reach_many(root: str, interval_list: Sequence[str]) -> list[str]:
    """Obtain nodes by repeatedly reaching up from :arg:`root`.

    Useful for building triads and scales from description.

    For each named interval in :arg:`interval_list`, call
    :code:`reach(root, interval)` and collect the result. At the
    end, return collected results in order.
    """
    return [reach(root, interval) for interval in interval_list]


def count_triad_major(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "major 3", "perfect 5"])


def count_triad_minor(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "minor 3", "perfect 5"])


def count_triad_augmented(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "major 3", "augmented 5"])


def count_triad_diminished(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "minor 3", "diminished 5"])


def invert(triad: list[str]) -> list[str]:
    return [*triad[1:], note_i2s(note_s2i(triad[0]) + len(NOTE_NAMES))]


def invert_triad_to(triad: list[str], note: str) -> list[str]:
    triad_without_octave = [match_out_numbers(x) for x in triad]

    note_without_octave = match_out_numbers(note)

    assert note_without_octave in triad_without_octave
    invert_by: int = triad_without_octave.index(note_without_octave)

    result: list[str] = triad
    for _ in range(invert_by):
        result = invert(result)

    return result


def triad(
    base_key: str,
    progression: list[int],
    add: int | list[int] = [],
    sus: int | list[int] = [],
    sharp: int | list[int] = [],
    flat: int | list[int] = [],
    intervals: str | list[str] = [],
    order: int = 0,
) -> list[str]:
    """Construct a triad.

    Args:
        add: Positions of notes in scale to add, 0 indexed.
        sus: Positions of notes in scale to remove, 0 indexed
        intervals: Positions of notes in scale to remove

    """
    scallion = scale(base_key, progression)

    degrees: list[int] = [0, 2, 4]

    # Add each of the `add`th degrees.
    if isinstance(add, int):
        add = [add]
    degrees += add

    # Remove each of the `sus`th degrees.
    if isinstance(sus, int):
        sus = [sus]
    for su in sus:
        degrees = [x for x in degrees if x != su]

    result: list[str] = []

    for d in degrees:
        result.append(
            note_i2s(
                note_s2i(scallion[(order + d) % len(scallion)])
                + len(NOTE_NAMES) * ((order + d) // len(scallion))
            )
        )

    # This is the "offset" caused by `order`\
    # of the first note from its original position.
    pegasus = note_s2i(result[0]) \
        + len(NOTE_NAMES) * (order // len(scallion)) \
        - note_s2i(scallion[0])

    # For each degree in `sharp`, add that note
    #   and shift it up by one half-step.
    if isinstance(sharp, int):
        sharp = [sharp]
    for s in sharp:
        result.append(note_i2s(
            note_s2i(scallion[s]) + 1 + pegasus))

    # For each degree in `flat`, add that note
    #   and shift it down by one half-step.
    if isinstance(flat, int):
        flat = [flat]
    for f in flat:
        result.append(note_i2s(
            note_s2i(scallion[f]) - 1 + pegasus))

    # Mechanically add every note that is a given interval
    #   from the tonic.
    if isinstance(intervals, str):
        intervals = [intervals]
    for interval in intervals:
        result.append(reach(base_key, INTERVALS[interval] + pegasus))

    if order > 0 and (intervals or sharp or flat):
        print(
            "Because `order` shifts the scale circularly"
            " in the space of scale degrees, features such as"
            " `intervals`, `sharp`, and `flat` may not"
            " produce the desired effect."
        )

    return sorted(result, key=lambda x: NOTES.index(x))


def seventh(
    base_key: str,
    progression: list[Interval],
    type: (
        Literal["major"]
        | Literal["minor"]
        | Literal["augmented"]
        | Literal["diminished"]
        | None
    ) = None,
    add: int | list[int] = [],
    sub: int | list[int] = [],
    intervals: str | list[str] = [],
    order: int = 0,
) -> list[str]:
    """ """
    if type is None:
        return triad(
            base_key,
            progression,
            intervals=intervals,
            add=[add, 6] if isinstance(add, int) else [*add, 6],
            sus=sub,
            order=order,
        )
    else:
        return triad(
            base_key,
            progression,
            intervals=[type + " 7", *intervals],
            add=add,
            sus=sub,
            order=order,
        )


def neapolitan_chord(base_key: str, intervals: list[Interval]) -> list[str]:

    return count_triad_major(
        note_i2s(note_s2i(scale(base_key, intervals)[1]) - 1)
    )


def count_seventh_dominant(root: str) -> list[str]:
    return [*count_triad_major(root), reach(root, "minor 7")]


def count_seventh_major(root: str) -> list[str]:
    return [*count_triad_major(root), reach(root, "major 7")]


def count_seventh_minor(root: str) -> list[str]:
    return [*count_triad_minor(root), reach(root, "minor 7")]


def count_seventh_half_diminished(root: str) -> list[str]:
    return [*count_triad_diminished(root), reach(root, "minor 7")]


def count_seventh_diminished(root: str) -> list[str]:
    return [*count_triad_diminished(root), reach(root, "diminished 7")]


def count_seventh_minor_major(root: str) -> list[str]:
    return [*count_triad_minor(root), reach(root, "major 7")]


def count_seventh_augmented_major(root: str) -> list[str]:
    return [*count_triad_augmented(root), reach(root, "major 7")]


def count_seventh_augmented_minor(root: str) -> list[str]:
    return [*count_triad_augmented(root), reach(root, "minor 7")]


def power(root: str) -> list[str]:
    """Return the power chord from :arg:`root`.

    A power chord has no major and minor qualities,
    because it always consists of the root and a
    perfect fifth.
    """
    return [root, reach(root, "perfect 5")]


def rewop(root: str) -> list[str]:
    """Inverse of :meth:`power`. Useful for,
    for example, adding bass to a note.
    """
    return [root, reach(root, -INTERVALS["perfect 5"])]
