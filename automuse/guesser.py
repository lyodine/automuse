"""Utilities that match notes with scales. Matching scales
contain the given notes, possibly in the exact order.

This is effectively a brute-force implementation of
chord-scale theory.
"""

from .modes import Interval
from .modes import MAJOR
from .modes import MINOR
from .modes import AUGMENTED
from .modes import DIMINISHED_WHOLE_HALF
from .modes import DIMINISHED_HALF_WHOLE
from .modes import MINOR_NATURAL
from .modes import MINOR_HARMONIC
from .modes import MINOR_MELODIC
from .modes import IONIAN
from .modes import DORIAN
from .modes import PHRYGIAN
from .modes import LYDIAN
from .modes import MIXOLYDIAN
from .modes import AEOLIAN
from .modes import LOCRIAN
from .modes import MAJOR_PENTATONIC
from .modes import MINOR_PENTATONIC
from .modes import MAJOR_BLUES
from .modes import MINOR_BLUES
from .modes import WHOLE_TONE

from .modes import TRIAD_MAJOR
from .modes import TRIAD_MINOR
from .modes import SEVENTH_MAJOR
from .modes import SEVENTH_MINOR
from .modes import SEVENTH_DOMINANT
from .modes import SEVENTH_DIMINISHED
from .modes import SEVENTH_MINOR_MAJOR
from .modes import SEVENTH_HALF_DIMINISHED
from .modes import SEVENTH_AUGMENTED_MAJOR
from .modes import SEVENTH_AUGMENTED
from .modes import SEVENTH_DIMINISHED_MAJOR

from . import extract_pitch_class, Degree

from collections.abc import Iterable
from .scale import scale
from .chord import chord, seventh, name_chord
from .transforms import invert_chord_by
from typing import NamedTuple, Literal, Sequence

from tabulate import tabulate

from automuse import NOTE_NAMES

type ModeSpec = tuple[list[Interval], str]

TEST_SCALES_STANDARD: tuple[ModeSpec, ...] = (
    (MAJOR, "M"),
    (MINOR, "m"),)

TEST_SCALES_MINORS: tuple[ModeSpec, ...] = (
    (MINOR_NATURAL, "m (Natural)"),
    (MINOR_HARMONIC, "m (Harmonic)"),
    (MINOR_MELODIC, "m (Melodic)"),)

TEST_SCALES_EXPANDED: tuple[ModeSpec, ...] = (
    (AUGMENTED, "A"),
    (DIMINISHED_WHOLE_HALF, "Dim W-H"),
    (DIMINISHED_HALF_WHOLE, "Dim H-W"),
    (MAJOR_PENTATONIC, "M (Pentatonic)"),
    (MINOR_PENTATONIC, "m (Pentatonic)"),
    (MAJOR_BLUES, "M (Blues)"),
    (MINOR_BLUES, "m (Blues)"),)

TEST_SCALES_EXOTIC: tuple[ModeSpec, ...] = (
    (WHOLE_TONE, "WholeTone"),)

TEST_SCALES_MODES: tuple[ModeSpec, ...] = (
    (IONIAN, "Ionian"),
    (DORIAN, "Dorian"),
    (PHRYGIAN, "Phrygian"),
    (LYDIAN, "Lydian"),
    (MIXOLYDIAN, "Mixolydian"),
    (AEOLIAN, "Aeolian"),
    (LOCRIAN, "Locrian"))

TEST_SCALES: tuple[ModeSpec, ...] =\
    TEST_SCALES_STANDARD +\
    TEST_SCALES_MINORS +\
    TEST_SCALES_EXPANDED +\
    TEST_SCALES_EXOTIC +\
    TEST_SCALES_MODES

TEST_TRIAD_MODES: tuple[ModeSpec, ...] = (
    (TRIAD_MAJOR, "M3"),
    (TRIAD_MINOR, "m3")
)

TEST_SEVENTH_MODES: tuple[ModeSpec, ...] = (
    (SEVENTH_MAJOR, "Δ7"),
    (SEVENTH_MINOR, "m7"),
    (SEVENTH_DOMINANT, "7"),
    (SEVENTH_DIMINISHED, "o7"),
    (SEVENTH_MINOR_MAJOR, "mM7"),
    (SEVENTH_HALF_DIMINISHED, "ø7"),
    (SEVENTH_AUGMENTED_MAJOR, "+7"),
    (SEVENTH_AUGMENTED, "7"),
    (SEVENTH_DIMINISHED_MAJOR, "oM")
)

TEST_CHORDS = TEST_TRIAD_MODES + TEST_SEVENTH_MODES

_IMMUTABLE_NOTE_NAMES = tuple(NOTE_NAMES)


#: Each item takes form (list[notes], key, mode)
type ScaleSpec = tuple[list[str], str, str]


class MatchResult(NamedTuple):
    #: Base note of the matched scale / chord
    key: str
    #: Mode of the matched scale / chord
    mode: str
    #: Matching notes
    matched: list[str]
    #: Notes that are in the subject, but not in the matched scale / chord
    unmatched: list[str]
    #: Notes that are in the matched scale / chord, but not in the subject
    unused: list[str]
    #: Notes to be matched
    check: list[str]
    #: Notes to be matched against
    against: list[str]


def guess_scale(notes: Sequence[str],
                mode_specs: Sequence[ModeSpec] = TEST_SCALES,
                roots: Sequence[str] = _IMMUTABLE_NOTE_NAMES,
                sort_key: Literal["matched"]
                | Literal["unused"]
                | Literal["unmatched"]
                | Literal["matched_percent"] =
                "matched",
                match_order: Literal["substring"]
                | Literal["order"]
                | Literal["any"] = "any") -> list[MatchResult]:
    """Check which scale or chord contain :arg:`subject`.

    Args:
        subject: A set of note classes, for example
            :code:`{"A", "A#"}`.

        test_scales: Interval patterns to compare
            :arg:`subject` against, for example
            :attr:`.TEST_SCALES_STANDARD`.

        roots: Note classes to construct :arg:`test_scales` on.
            The default :attr:`NOTE_NAMES` contains all note
            classes.

        sort_key: How the returned list is sorted. See
            attributes of :class:`MatchResult` for what the
            available values mean. Also, ``matched_percent``
            uses the ratio of matched notes against unused
            notes.

        match_order: How :arg:`notes` is checked against
            :arg:`test_modes`:

            * ``"substring"``: Match the longest substring
                of :arg:`notes`.

            * ``"order"``: Match notes in :arg:`notes` in order,
                moving on to the next once a note is matched.

            * ``"any"``: Match any note that occur in
                :arg:`notes`.
    """
    test_scales: list[ScaleSpec] = []

    for key in roots:
        for mode, mode_name in mode_specs:
            test_scales.append(
                (scale(key, mode),
                 key,
                 mode_name)
            )

    return guess(check=notes,
                 test_scales=test_scales,
                 sort_key=sort_key,
                 match_order=match_order)


def guess_chord(
        notes: Iterable[str],
        mode_specs: Iterable[ModeSpec] = TEST_SCALES,
        tonics: Iterable[str] = _IMMUTABLE_NOTE_NAMES,
        chords: Iterable[
            Literal["triad"]
            | Literal["seventh"]] = ("triad", "seventh"),
        orders: Iterable[Degree] = (0, 1, 2, 3, 4, 5, 6, 7),
        inversions: Sequence[int] = (0, 1, 2, 3),
        sort_key: Literal["matched"]
        | Literal["unused"]
        | Literal["unmatched"]
        | Literal["matched_percent"] =
        "matched",
        match_order: Literal["substring"]
        | Literal["order"]
        | Literal["any"] = "any") -> list[MatchResult]:
    """Convenience function that guess which chords
    contain :arg:`notes`.

    This function can guess against:

    * Triads

    * Seventh chords of all qualities (major,
      minor, augmented, diminished)

    * Modes (e.g. M, m, Dorian)

    * Inversions

    * Orders (e.g. :math:`\\textrm{I}`)

    It cannot guess against:

    * Add, sus, sharp, and flat chords

    * Extra notes by intervals (e.g. b6)

    * Extended chords above seventh

    For a more powerful guesser, consider
    :meth:`guess_scale` with :attr:`TEST_CHORDS`.

    Args:
        tonics: See :meth:`.chord`.
        mode_specs: See :meth:`.guess_scale`.
        chords: Can be :code:`"triad"`, :code:`"seventh"`, or
            both.
        orders: See :meth:`.chord`.
        inversions: See :meth:`.chord`.
        sort_key: See :meth:`.guess_scale`.
        match_order: See :meth:`.guess_scale`.
    """
    test_scales: list[ScaleSpec] = []
    # Oh no so many indentations! It's too much!
    for tonic in tonics:
        for mode, mode_name in mode_specs:
            for order in orders:
                if "triad" in chords:
                    chord_actual: list[str] = chord(
                        tonic=tonic,
                        mode=mode,
                        order=order,
                    )
                    for invert_by in inversions[:3]:
                        chord_notes: list[str] = invert_chord_by(
                            chord_actual,
                            invert_by)
                        chord_name: str = name_chord(
                            tonic=tonic,
                            order=order,
                            chord_type="triad",
                            mode_name=mode_name,
                            inversion=invert_by,
                            include_tonic=False)
                        test_scales.append((chord_notes, tonic, chord_name))
                    if "seventh" in chords:
                        for seventh_type in [None,
                                             "major",
                                             "minor",
                                             "augmented",
                                             "diminished"]:
                            chord_actual: list[str] = seventh(
                                tonic=tonic,
                                mode=mode,
                                order=order,
                                type=seventh_type,
                            )
                            for invert_by in inversions[:3]:
                                chord_notes: list[str] = invert_chord_by(
                                    chord_actual,
                                    invert_by)
                                chord_name: str = name_chord(
                                    tonic=tonic,
                                    order=order,
                                    chord_type="triad",
                                    mode_name=mode_name,
                                    inversion=invert_by,
                                    seventh_type=seventh_type,
                                    include_tonic=False)
                                test_scales.append((chord_notes,
                                                    tonic,
                                                    chord_name))

    return guess(check=notes,
                 test_scales=test_scales,
                 sort_key=sort_key,
                 match_order=match_order)


def guess(check: Iterable[str],
          test_scales: list[ScaleSpec],
          sort_key:
          Literal["matched"]
          | Literal["unused"]
          | Literal["unmatched"]
          | Literal["matched_percent"],
          match_order:
          Literal["substring"]
          | Literal["order"]
          | Literal["any"])\
        -> list[MatchResult]:
    """Helper function. Check :arg"`check` against
    scales or chords in :arg:`against`.

    This function is a big dispatcher: it has
    several options (:arg:`sort_key`) and
    (:arg:`match_order`). Beware of that.

    See :meth:`.guess_scale` for arguments.
    """
    check = [extract_pitch_class(x) for x in check]

    match_result: list[MatchResult] = []

    match match_order:
        case "substring":
            for notes, key, mode in test_scales:
                notes = [extract_pitch_class(x) for x in notes]
                match_result.append(
                    _match_substring(check, notes, key, mode)
                )
        case "order":
            for notes, key, mode in test_scales:
                notes = [extract_pitch_class(x) for x in notes]
                match_result.append(
                    _match_order(check, notes, key, mode)
                )
        case "any":
            check_set: set[str] = set(check)
            for notes, key, mode in test_scales:
                notes = [extract_pitch_class(x) for x in notes]
                against_set = set(notes)
                match_result.append(
                    MatchResult(
                        key,
                        mode,
                        matched=list(check_set.intersection(against_set)),
                        unmatched=list(check_set.difference(against_set)),
                        unused=list(against_set.difference(check_set)),
                        check=check,
                        against=notes))
        case _:
            raise ValueError(f"Order {match_order} not recognised")

    match sort_key:
        case "matched":
            _k = lambda x: len(x.matched)
        case "unused":
            _k = lambda x: -len(x.unused)
        case "unmatched":
            _k = lambda x: -len(x.unmatched)
        case "matched_percent":
            _k = lambda x: len(x.matched) / (len(x.matched) + len(x.unmatched))
        case _:
            raise ValueError(f"Sort key {sort_key} not recognised")

    return sorted(match_result,
                  key=_k,
                  reverse=True)


def _match_substring(check: list[str],
                     against: list[str],
                     key: str,
                     mode: str) -> MatchResult:
    """Match the longest substring of :arg:`check`
    starting at index 0. For example, matching
    :code:`["A", "B"]` against :code:`["C", "A", "C", "B"]`
    gives :code:`["A"]`.
    """
    match_start: int
    match_length: int
    # There is a small performance loss: Because :arg:`against`
    #   is indexed anyway if ``check[0] in against``, a more
    #   efficient approach would be to try :meth:`list.index`,
    #   then wait for an ValueError if ``check[0]`` is not in
    #   the list.
    # Not worth sacrificing readability, though it irks me to
    #   (knowingly) take the inefficient approach.
    if check[0] in against:
        i: int = 0
        j: int = against.index(check[0])
        match_start = j
        for i, note in enumerate(check):
            # If _notes is exhausted, or if the next item
            #   does not match, return with :code:`i`.

            if i + j >= len(against)\
                    or against[i + j] != note:
                i = i - 1
                break
        match_length = i + 1
    else:
        # No match at all
        match_start = 0
        match_length = 0

    return MatchResult(
        key=key,
        mode=mode,
        matched=check[:match_length],
        unmatched=check[match_length:],
        unused=against[0:match_start]
        + against[match_start + match_length:],
        check=check,
        against=against,
    )


def _match_order(check: list[str],
                 against: list[str],
                 key: str,
                 mode: str) -> MatchResult:
    """Check :arg:`check` against :arg:`against` in
    order, RegEx style.

    I don't really feel like typing right now, so
    you (and my future self) are on your own with this one.

    Similar to :meth:`._match_substring`, except that the
    match does not need to be an exact substring of
    :arg:`check`; instead, it only needs to be in the same order.

    Arguments :arg:`key` and :arg:`mode` are only used to
    construct a :class:`MatchResult`.
    """
    if check[0] in against:
        i: int = 0
        j: int = against.index(check[0])
        matched_js: set[int] = set()
        for i, note in enumerate(check):
            # Must be a better way to implement this.
            if j >= len(against):
                break
            # Continue incrementing j, until :arg:`against`
            #   lines up with :arg:`check`.
            while j < len(against) and against[j] != note:
                j += 1

            if j < len(against) and against[j] == note:
                matched_js.add(j)
                j += 1

        return MatchResult(
            key=key,
            mode=mode,
            matched=check[:len(matched_js)],
            unmatched=check[len(matched_js):],
            unused=[against[nj] for nj in range(len(against))
                    if nj not in matched_js],
            check=check,
            against=against,
        )
    else:
        return MatchResult(
            key=key,
            mode=mode,
            matched=[],
            unused=against.copy(),
            unmatched=check.copy(),
            check=check,
            against=against,
        )


def tabulate_guess(result: list[MatchResult],
                   tablefmt: str = "simple") -> None:
    return tabulate(result,
                    headers=["Key",
                             "Mode",
                             "Matched",
                             "Unmatched",
                             "Unused",
                             "Check",
                             "Against"],
                    tablefmt=tablefmt,
                    colalign=["left"] * 7)
