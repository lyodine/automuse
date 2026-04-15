"""Utilities that construct chords.
"""
# Legacy, find an alternative.
from .counted import count_triad_major

from .. import (
    INTERVALS,
    NOTE_NAMES,
    NOTES,
    Interval,
    Degree,
    note_i2s,
    note_s2i,
    reach,
)

from typing import Literal

from ..scale import scale


def chord(
    tonic: str,
    mode: list[Interval],
    order: int = 0,
    add: Degree | list[Degree] | None = None,
    sus: Degree | list[Degree] | None = None,
    sharp: Degree | list[Degree] | None = None,
    flat: Degree | list[Degree] | None = None,
    raw_offsets: str | list[str] | None = None,
) -> list[str]:
    """Construct a chord from a scale. Construct a triad by default.

    Args:
        tonic: Root of the chord.
        mode: Mode of the chord, for example :attr:`.modes.MAJOR`.
        order: Order of the chord, for example 1 for :math:`\\text{I}`.
        add: Scale degrees to add, 0 indexed.
        sus: Scale degrees to remove, 0 indexed.
        sharp: Scale degrees to add then raise by one semitone.
        flat: Scale degrees to add then lower by one semitone.
        raw_offsets: Extra notes to add to the chord, specified
            as semitone offsets from the tonic. Last resort.
        order: Order of scale. For example, 0 means :math:`\\text{I}`
            and 1 means :math:`\\text{II}`

    """
    def _init_list_if_none[T](what: T | list[T] | None)\
            -> T | list[T]:
        return [] if what is None else what

    add = _init_list_if_none(add)
    sus = _init_list_if_none(sus)
    sharp = _init_list_if_none(sharp)
    flat = _init_list_if_none(flat)
    raw_offsets = _init_list_if_none(raw_offsets)

    scallion = scale(tonic, mode)

    degrees: list[Degree] = [0, 2, 4]

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
    if isinstance(raw_offsets, str):
        raw_offsets = [raw_offsets]
    for interval in raw_offsets:
        result.append(reach(tonic, INTERVALS[interval] + pegasus))

    if order > 0 and (raw_offsets or sharp or flat):
        # Removing for now.
        # logging.warning(
        #     "Because `order` shifts the scale circularly"
        #     " in the space of scale degrees, features that"
        #     " use raw semitones (e.g. `intervals`, `sharp`,"
        #     " and `flat`) may not work correctly."
        # )
        pass

    return sorted(result, key=lambda x: NOTES.index(x))


def seventh(
    tonic: str,
    mode: list[Interval],
    type: (
        Literal["major"]
        | Literal["minor"]
        | Literal["augmented"]
        | Literal["diminished"]
        | None
    ) = None,
    add: int | list[int] | None = None,
    sus: int | list[int] | None = None,
    sharp: Degree | list[Degree] | None = None,
    flat: Degree | list[Degree] | None = None,
    raw_offsets: str | list[str] | None = None,
    order: int = 0,
) -> list[str]:
    """Construct a seventh chord from a scale. Can
    add custom :math:`\\hat{7}`\\ s.

    See :meth:`.chord` for parameters.
    """
    # Necessary to make unpacking later easier.
    # Otherwise unpacking would need to check for None.
    add = [] if add is None else add
    raw_offsets = [] if raw_offsets is None else raw_offsets
    if type is None:
        return chord(
            tonic,
            mode,
            raw_offsets=raw_offsets,
            add=[add, 6] if isinstance(add, int) else [*add, 6],
            sus=sus,
            sharp=sharp,
            flat=flat,
            order=order,
        )
    else:
        return chord(
            tonic,
            mode,
            raw_offsets=[type + " 7", *raw_offsets],
            add=add,
            sus=sus,
            sharp=sharp,
            flat=flat,
            order=order,
        )


def neapolitan_chord(tonic: str,
                     intervals: list[Interval]) -> list[str]:
    """Construct a Neapolitan chord from a scale.
    """

    return count_triad_major(
        note_i2s(note_s2i(scale(tonic, intervals)[1]) - 1)
    )


def power(root: str) -> list[str]:
    """Construct the power chord of :arg:`root`.

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


INVERSION_NAMES_MAP = {
    "triad": ("", "⁶", "⁶₄"),
    "seventh": ("⁷", "⁶₅", "⁴₃", "²")
}

ORDER_NAMES = (
    "I", "II", "III", "IV", "V",
    "VI", "VII", "VIII", "IX", "X",
)

SEVENTH_TYPES_MAP = {
    None: "",
    "major": "ᴹ",
    "minor": "ᵐ",
    "augmented": "⁺",
    "diminished": "ᵈ"
}


def name_chord(
    tonic: str,
    mode_name: str,
    order: int,
    chord_type:
    Literal["triad"]
    | Literal["seventh"],
    inversion: int,
    seventh_type: Literal["major"]
    | Literal["minor"]
    | Literal["augmented"]
    | Literal["diminished"]
    | None = None,
    include_tonic: bool = True
) -> str:
    return tonic if include_tonic else "" + mode_name\
        + SEVENTH_TYPES_MAP[seventh_type]\
        + INVERSION_NAMES_MAP[chord_type][inversion]\
        + f"({ORDER_NAMES[order]})"
