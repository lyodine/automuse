"""Transforms, or transformations.
From inversion and transposition to the
neo-Riemannian school of transforms.

Neo-Riemannian transforms are implemented
referencing //Hollywood Harmony// by Lehman.
"""
from typing import overload, Literal, Callable
from . import Note
from . import Interval
from . import NOTES
from . import NOTE_NAMES
from . import note_i2s
from . import note_s2i
from . import interval_s2i
from . import extract_pitch_class
from . import get_interval
from . import reach
from . import chord as chord
from . import modes as modes


@overload
def invert(arg: str) -> str:
    pass


@overload
def invert(arg: Interval | Note) -> Interval | Note:
    pass


def invert(arg: Interval | Note | str) -> Note | Interval | str:
    """Invert an interval. Or a note.

    Works with both because taking the
    modular complement happens to have the
    same effect on both.
    """
    if isinstance(arg, int):
        return (len(NOTE_NAMES) - arg) % len(NOTES)
    else:
        return note_i2s((len(NOTE_NAMES) - note_s2i(arg))
                        % len(NOTES))


def invert_chord(notes: list[str]) -> list[str]:
    """Invert :arg:`notes` by 1.
    """
    return invert_chord_by(notes, 1)


def invert_chord_by(notes: list[str], invert_by: int) -> list[str]:
    """Invert :arg:`notes` by :arg:`invert_by`.
    """
    invert_by_octaves: int = \
        int(math.copysign((abs(invert_by) // len(notes)),
                          invert_by))
    invert_by = int(math.copysign((abs(invert_by) % len(notes)),
                                  invert_by))

    # Documentation is for the weak
    hedon: list[str] = transpose(notes[:invert_by], 12)\
        if invert_by > 0 else notes[:invert_by]

    dolor: list[str] = transpose(notes[invert_by:], -12)\
        if invert_by < 0 else notes[invert_by:]

    oll = transpose(dolor + hedon, invert_by_octaves * 12)

    return oll


def invert_chord_to(notes: list[str],
                    note: str) -> list[str]:
    """Invert :arg:`notes` to :arg:`note`. In other
    words, slash chord.

    Can only transpose up.

    Degree of inversion is computed with the note
    class of :arg:`note`; its octave does not matter.
    """
    notes = sorted(notes, key=note_s2i)
    triad_without_octave = [extract_pitch_class(x) for x in notes]
    note_without_octave = extract_pitch_class(note)
    assert note_without_octave in triad_without_octave

    invert_by: int =\
        triad_without_octave.index(note_without_octave)

    return invert_chord_by(notes, invert_by)


@overload
def transpose(note: str,
              by: int) -> str:
    pass


@overload
def transpose(note: list[str],
              by: int) -> list[str]:
    pass


def transpose(note: str | list[str],
              by: int) -> str | list[str]:
    """Transpose a note or notes by semitones.
    """
    if isinstance(note, str):
        return note_i2s(note_s2i(note) + by)
    else:
        return [transpose(n, by) for n in note]


def _is_major_triad(triad: list[str]) -> bool:
    return get_interval(triad[0], triad[1])\
        == interval_s2i("major 3") \
        and get_interval(triad[0], triad[2])\
        == interval_s2i("perfect 5")


def _is_minor_triad(triad: list[str]) -> bool:
    return get_interval(triad[0], triad[1])\
        == interval_s2i("minor 3")\
        and get_interval(triad[0], triad[2])\
        == interval_s2i("perfect 5")


def _nrt_transform_helper(
        triad: list[str],
        result_if_major: Callable[[], list[str]],
        result_if_minor: Callable[[], list[str]])\
        -> list[str]:
    """Helper function for implementing
    neo-Riemannian transforms. If :arg:`triad`
    is major, return :arg:`result_if_major`.
    Else, if :arg:`triad` is minor, return
    :arg:`result_if_minor`. Otherwise, raise
    an exception.

    Taking nullary functions, instead of values,
    in :arg:`result_if_major` and
    :arg:`result_if_minor` allows them the be
    lazily evaluated.

    Raises:
        ValueError: If :arg:`triad` is neither
        major nor minor.
    """
    triad = sorted(triad, key=lambda x: note_s2i(x))

    if _is_major_triad(triad):
        return result_if_major()
    elif _is_minor_triad(triad):
        return result_if_minor()
    else:
        raise ValueError(f"{triad} not a major/minor triad.")


def nrt_parallel(triad: list[str]) -> list[str]:
    """The parallel transform (**P**) maps
    a major triad to its minor.
    """
    return _nrt_transform_helper(
        triad,
        lambda: [triad[0], transpose(triad[1], -1), triad[2]],
        lambda: [triad[0], transpose(triad[1], 1), triad[2]]
    )


def nrt_relative(triad: list[str]) -> list[str]:
    """The relative transform (**R**) maps
    a major triad to its relative minor, and a
    minor triad to its relative major.
    """
    return _nrt_transform_helper(
        triad,
        lambda: [reach(triad[0], "major 3", reverse=True),
                 reach(triad[1], "minor 3", reverse=True),
                 reach(triad[2], "major 3", reverse=True)],
        lambda: [reach(triad[0], "minor 3"),
                 reach(triad[1], "major 3"),
                 reach(triad[2], "minor 3")]
    )


def nrt_slide(triad: list[str]) -> list[str]:
    """The slide transform (**S**) maps a major
    triad to the minor triad one semitone higher.
    """
    return _nrt_transform_helper(
        triad,
        lambda: chord.chord(
            transpose(triad[0], 1), modes.MINOR),
        lambda: chord.chord(
            transpose(triad[0], -1), modes.MAJOR),
    )


def nrt_leading_tone_exchange(triad: list[str]) -> list[str]:
    """The leading tone exchange (**L**,
    Leittonwechselklänge) transform maps
    a major triad to the minor triad a major
    third higher.
    """
    return _nrt_transform_helper(
        triad,
        lambda: [reach(triad[0], "major 3"),
                 reach(triad[1], "minor 3"),
                 reach(triad[2], "major 3")],
        lambda: [reach(triad[0], "major 3", reverse=True),
                 reach(triad[1], "minor 3", reverse=True),
                 reach(triad[2], "major 3", reverse=True)]
    )


def _nrt_fifth_helper(
        triad: list[str],
        specs: dict[Literal["major"] | Literal["minor"],
                    tuple[str, bool, list[Interval]]])\
        -> list[str]:
    """Helper function for building \\*-fifth transforms.
    :arg:`specs` has form
    :code:`("major"|"minor": (interval, inverse, quality))`
    """
    return _nrt_transform_helper(
        triad,
        lambda: chord.chord(
            reach(triad[0],
                  *specs["major"][:2]),
            specs["major"][2]
        ),
        lambda: chord.chord(
            reach(triad[0],
                  *specs["minor"][:2]),
            specs["minor"][2]
        ))


def nrt_near_fifth(triad: list[str]) -> list[str]:
    """The near fifth (**N**) transform maps a major triad
    to its fifth minor, and a minor triad to its
    fifth major.
    """
    return _nrt_fifth_helper(
        triad,
        {"major": ("perfect 4", False, modes.MINOR),
         "minor": ("perfect 4", True, modes.MAJOR)}
    )


def nrt_far_fifth(triad: list[str]) -> list[str]:
    """The far fifth (**F**) transform maps a major triad
    to its fourth minor, and a minor triad to its
    fourth major.
    """
    return _nrt_fifth_helper(
        triad,
        {"major": ("perfect 5", False, modes.MINOR),
         "minor": ("perfect 5", True, modes.MAJOR)}
    )


def nrt_dominant(triad: list[str],
                 inverse: bool = False) -> list[str]:
    """The dominant transform (**N**) maps a
    triad to its fifth with the same quality.

    Note that this will only raise, and never lower, the root.
    Set :arg:`inverse` to `True` to map back.
    """
    if inverse:
        return _nrt_fifth_helper(
            triad,
            {"major": ("perfect 5", False, modes.MAJOR),
             "minor": ("perfect 5", False, modes.MINOR)}
        )
    else:
        return _nrt_fifth_helper(
            triad,
            {"major": ("perfect 4", True, modes.MAJOR),
             "minor": ("perfect 4", True, modes.MINOR)}
        )


def nrt_hexatonic_pole(triad: list[str]) -> list[str]:
    """The hexatonic pole (H) maps a major triad
    to the triad that is a major 3 before it.

    Source: `Audacious Euphony`.
    """
    return _nrt_transform_helper(
        triad,
        lambda: chord.chord(reach(triad[0], "major 3", True),
                            modes.MINOR),
        lambda: chord.chord(reach(triad[0], "major 3"),
                            modes.MAJOR),
    )


def nrt_t6(triad: list[str], up: bool = True) -> list[str]:
    """The T6 transform transposes all notes in
    a chord by 6 semitones. That's half an octave.

    Source: `Neo-Riemannian examples in music <SS>`_

    .. _SS: <https://alpof.wordpress.com/2021/10/09/
        neo-riemannian-examples-in-music/>`
    """
    return transpose(triad, 6 if up else -6)
