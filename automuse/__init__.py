"""Definition of the pitch space, notes, intervals,
and basic operations on them.
"""


from typing import overload, Sequence, Optional
import collections
import re

"""In this text, a number can mean one of
three things:

1. A note (2 for "Re", or D).
2. An interval in semitones (2 for "two notes from the previous note").
3. An offset from the root / tonic in semitones
   ("two semitones above the root").
4. A scale degree ("second note in a scale").

To differentiate these cases, type signatures should
use the following aliases in place of `int`.
"""

#: Interval. Difference between notes in semitones.
Interval = int
#: Offset from tonic / root to a note.
Offset = int
#: Pitch. Index in :attr:`.NOTES`.
Note = int
#: Scale degree
Degree = int


def note_m2s(note: Note) -> str:
    """Map an index to its value in :attr:`.NOTES_MIDI`.

    Unlike :meth:`.note_i2s`, this function always uses
    :attr:`.NOTES_MIDI`.
    """
    assert note >= 0 and note <= 127, \
        "Note outside of MIDI range"

    return NOTE_NAMES[note % len(NOTE_NAMES)]\
        + str(note // len(NOTE_NAMES))


def note_s2m(note: str) -> Note:
    """Map a name to its index in :attr:`.NOTES_MIDI`.

    Unlike :meth:`.note_s2i`, this function always uses
    :attr:`.NOTES_MIDI`.
    """
    assert re.match("[0-9]", note[-1]), \
        "Specification does not include octave"

    assert note[:-1] in NOTE_NAMES, \
        f"{note[:-1]} is not in `NOTES`"

    return 12 * int(note[-1]) + NOTE_NAMES.index(note[:-1])


@overload
def note_i2s(note: Optional[Note]) -> str:
    pass


@overload
def note_i2s(note: Sequence[Optional[Note]]) -> list[str]:
    pass


def note_i2s(note: Optional[Note]
             | Sequence[Optional[Note]]) -> str | list[str]:
    """Map an index or sequence of indices
    to names in :attr:`.NOTES`.
    """

    def _base(key_int: Optional[Note]) -> str:
        if key_int is None:
            return " "
        else:
            return NOTES[key_int % len(NOTES)]

    if note is None:
        return " "
    if isinstance(note, Note):
        # Safeguard not needed.
        # if note > 127 or note < 0:
        #     raise ValueError(f"MIDI does not support note {note}")
        return _base(note)
    else:
        return [_base(kn) for kn in note]


@overload
def note_s2i(name: str,
             solfege: bool = False) -> Note:
    pass


@overload
def note_s2i(name: list[str],
             solfege: bool = False) -> list[Note]:
    pass


def note_s2i(name: str | list[str],
             solfege: bool = False) -> Note | list[Note]:
    """Map a name or sequence of names
    to indices of :attr:`.NOTES`.
    """

    def _base(name: str) -> Note:
        sofege_offset: int = 1 if solfege else 0
        if name in NOTES:
            return NOTES.index(name) + sofege_offset
        else:
            return NOTE_NAMES.index(name) + sofege_offset

    if isinstance(name, str):
        return _base(name)
    else:
        return [_base(kn) for kn in name]


#: Names of note classes.
NOTE_NAMES: tuple[str, ...] = (
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)


# Limited to 121 notes, this makes modular math work.
NOTES_MIDI: tuple[str, ...] = tuple(note_m2s(i) for i in range(0, 120))


NOTES_CLASS: tuple[str, ...] = NOTE_NAMES


NOTES: tuple[str, ...] = NOTES_MIDI


def _initialise_intervals() -> dict[str, int]:
    """Machinery. Initialise :attr:`.INTERVALS`.
    """

    # Map of each semitone difference to a name. The entry
    # `difference`: (`major/minor`, `number`) means
    # `difference` is the `major/minor` `number`
    # :sup:`th`.

    interval_seeds: dict[int, tuple[str, int]] = {
        2: ("major", 2),
        4: ("major", 3),
        5: ("perfect", 4),
        7: ("perfect", 5),
        9: ("major", 6),
        11: ("major", 7),
        12: ("perfect", 8),
    }

    # from each perfect, produce: augmented +1, diminished -2
    result: dict[str, int] = dict()
    result["prime 1"] = 0
    result["augmented 1"] = 1
    result["diminished 1"] = 11
    for interval_semitone, (name, order) in interval_seeds.items():
        if name == "major":
            # from each major, produce: augmented +1, minor -1, diminished -2
            result[f"augmented {order}"] =\
                (interval_semitone + 1)  # % len(result)
            result[f"major {order}"] =\
                interval_semitone
            result[f"minor {order}"] =\
                (interval_semitone - 1)  # % len(result)
            # Diminishing a minor gives -2 from major
            result[f"diminished {order}"] =\
                (interval_semitone - 2)  # % len(result)
        elif name == "perfect":
            result[f"augmented {order}"] =\
                (interval_semitone + 1)  # % len(result)
            result[f"perfect {order}"] =\
                (interval_semitone) % len(result)
            result[f"diminished {order}"] =\
                (interval_semitone - 1)  # % len(result)
        else:
            raise KeyError()
    return result


INTERVALS: dict[str, int] = _initialise_intervals()


def interval_s2i(name: str) -> Interval:
    """Map a interval name (e.g. :code:`major 2`)
    to a semitone difference.
    """
    return INTERVALS[name]


def interval_i2s(key_num: Interval) -> list[str]:
    """Map a semitone difference to a list
    of possible nams. Does not consider the generic
    interval.
    """
    return [
        name
        for name, interval_semitone in INTERVALS.items()
        if interval_semitone == key_num
    ]


def get_interval(note_from: str, note_to: str) -> int:
    """Take two notes and return the interval between
    them, in semitones.
    """

    return note_s2i(note_to) - note_s2i(note_from)


def name_interval(note_from: str, note_to: str) -> str:
    """Take two notes and return the name of their
    interval.
    """

    interval_semitone = get_interval(note_from, note_to)\
        % len(NOTE_NAMES)

    interval_major = str(
        (ord(note_to[0]) - ord(note_from[0]))
        % (ord("G") - ord("A") + 1) + 1
    )

    possible_intervals = interval_i2s(interval_semitone)

    matching_names: list[str] = [
        x for x in possible_intervals if x[-1] == interval_major
    ]

    assert len(matching_names) < 2

    return matching_names[0]


def reach(root: str,
          interval: str | int,
          reverse: bool = False) -> str:
    """ "Reach up" from :arg:`tonic` by
    :arg:`interval`. :arg:`interval` can be
    either a number (e.g. 1) or a string
    (e.g. :code:`"augmented 8"`).

    In the latter case, :arg:`interval` should be a
    key in :attr:`INTERVALS`.
    """
    apartness: int
    if isinstance(interval, str):
        apartness = INTERVALS[interval]
    else:
        apartness = interval

    if reverse:
        apartness = -apartness

    return note_i2s((note_s2i(root) + apartness) % len(NOTES))


def reach_many(root: str, interval_list: Sequence[str]) -> list[str]:
    """Obtain nodes by repeatedly reaching up from :arg:`root`
    by intervals in :arg:`interval_list`.

    Useful for building triads and scales from intervals.
    """
    return [reach(root, interval) for interval in interval_list]


def extract_pitch_class(expr: str) -> str:
    """Map a note in IPN to its pitch class.

    For example, :code:`"C#4"` maps to :code:`"C#"`.
    """
    manah: Optional[re.Match] = re.match("((?![0-9]).)*", expr)

    if manah:
        return manah.group(0)
    else:
        raise Exception("owo")


def extract_octave(expr: str) -> int:
    """Map a note in IPN to its octave.

    For example, calling with :code:`"C#4"` yields 4.
    """
    manah: Optional[re.Match] = re.match("((?![0-9]).)(([0-9]).)", expr)

    if manah:
        return int(manah.group(2))
    else:
        raise Exception("owo")


@overload
def same_class(a: list[str], b: list[str]) -> bool:
    pass


@overload
def same_class(a: str, b: str) -> bool:
    pass


def same_class(a: list[str] | str,
               b: list[str] | str) -> bool:
    """Return if :arg:`a` and :arg:`b` belong to the same
    pitch class.
    """

    if isinstance(a, str) and isinstance(b, str):
        return extract_pitch_class(a) == extract_pitch_class(b)
    else:

        a = [extract_pitch_class(x) for x in a]
        b = [extract_pitch_class(x) for x in b]

        return collections.Counter(a) == collections.Counter(b)
