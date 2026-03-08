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

from .modes import TRIAD
from .modes import SEVENTH_MAJOR
from .modes import SEVENTH_MINOR
from .modes import SEVENTH_AUGMENTED
from .modes import SEVENTH_DIMINISHED

from .chord import scale
from typing import NamedTuple, Literal

from tabulate import tabulate

from omusic import NOTE_NAMES

type ScaleSpec = list[tuple[list[Interval], str]]

TEST_SCALES_STANDARD = [
    (MAJOR, "major"),
    (MINOR, "minor"),]

TEST_SCALES_MINORS = [
    (MINOR_NATURAL, "natural minor"),
    (MINOR_HARMONIC, "harmonic minor"),
    (MINOR_MELODIC, "melodic minor"),]

TEST_SCALES_EXPANDED = [
    (AUGMENTED, "augmented"),
    (DIMINISHED_WHOLE_HALF, "diminished, whole half"),
    (DIMINISHED_HALF_WHOLE, "diminished, half whole"),
    (MAJOR_PENTATONIC, "pentatonic major"),
    (MINOR_PENTATONIC, "pentatonic minor"),
    (MAJOR_BLUES, "blues major"),
    (MINOR_BLUES, "blues minor")]

TEST_SCALES_MODES = [
    (IONIAN, "ionian"),
    (DORIAN, "dorian"),
    (PHRYGIAN, "phrygian"),
    (LYDIAN, "lydian"),
    (MIXOLYDIAN, "mixolydian"),
    (AEOLIAN, "aeolian"),
    (LOCRIAN, "locrian")]

TEST_CHORDS = [
    (TRIAD, "triad"),
    (SEVENTH_MAJOR, "major seventh"),
    (SEVENTH_MINOR, "minor seventh"),
    (SEVENTH_AUGMENTED, "augmented seventh"),
    (SEVENTH_DIMINISHED, "diminished seventh")]

TEST_SCALES = TEST_SCALES_STANDARD +\
    TEST_SCALES_MINORS +\
    TEST_SCALES_EXPANDED +\
    TEST_SCALES_MODES


class MatchResult(NamedTuple):
    #: Base note of the matched scale / chord
    base: str
    #: Mode of the matched scale / chord
    mode: str
    #: Matching notes
    matched: set[str]
    #: Notes that are in the matched scale / chord, but not in the subject
    unused: set[str]
    #: Notes that are in the subject, but not in the matched scale / chord
    unmatched: set[str]


def guess(subject: set[str],
          test_scales: ScaleSpec,
          sort_key: Literal["matched"]
          | Literal["unused"]
          | Literal["unmatched"]
          | Literal["matched_percent"] =
          "matched") -> list[MatchResult]:
    """Check which scale or chord may be have produced
    :arg:`subject`.

    The returned list is ordered by :arg:`sort_key`. See
    :class:`MatchResult` for options. ``matched_percent``
    uses the ratio of matched notes against unused
    notes.

    Args:
        subject: A set of note classes
        test_scales: Scales and chords to compare
            :arg:`subject` against
    """
    list_of_scales: list[MatchResult] = []
    for key in NOTE_NAMES:
        for _scale in test_scales:
            this_scale_set = set([x[:-1] for x in scale(key, _scale[0])])
            that_scale_set = subject
            list_of_scales.append(
                MatchResult(
                    key,
                    _scale[1],
                    this_scale_set.intersection(that_scale_set),
                    this_scale_set.difference(that_scale_set),
                    that_scale_set.difference(this_scale_set)))

    if sort_key == "matched":
        _k = lambda x: len(x[2])
    elif sort_key == "unused":
        _k = lambda x: -len(x[3])
    elif sort_key == "unmatched":
        _k = lambda x: -len(x[4])
    elif sort_key == "matched_percent":
        _k = lambda x: len(x[2]) / (len(x[2]) + len(x[3]))
    else:
        raise ValueError(f"Sort key {sort_key} not recognised")
    return sorted(list_of_scales,
                  key=_k,
                  reverse=True)


def tabulate_guess(result: list[MatchResult],
                   tablefmt: str = "simple") -> None:
    return tabulate(result,
                    headers=["Base",
                             "Mode",
                             "Matched",
                             "Unused",
                             "Unmatched"],
                    tablefmt=tablefmt,
                    colalign=["left",
                              "left",
                              "left",
                              "left",
                              "left"])
