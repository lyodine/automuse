"""In this text, a number can mean one of
three things:

1. A note (2 for "Re", or D).
2. An interval (2 for "two notes from the previous note").
3. An offset ("two notes from the first note").

To differentiate these, use type "aliases"
defined in the following cell instead of `int`.
"""

from typing import overload, Sequence, Optional
import collections
import re


"""An interval. The interval from
the :math:`a`\\ :sup:`th` note and the
:math:`b`\\ :sup:`th` is :math:`b-a`.
"""
Interval = int
Pitch = int

"""A pitch, representing
a note by its position in :attr:`NOTES`.
"""
Note = int


def note_m2s(note: int) -> str:
    """ """
    assert note >= 0 and note <= 127, \
        "Note outside of MIDI range"

    return NOTE_NAMES[note % len(NOTE_NAMES)]\
        + str(note // len(NOTE_NAMES))


def note_s2m(note: str) -> int:
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
    """Return either a string or a list
    of strings that represents note(s) in
    :arg:`note`.
    """

    def _base(key_int: Optional[Note]) -> str:
        if key_int is None:
            return " "
        else:
            return NOTES[key_int % len(NOTES)]

    if note is None:
        return " "
    if isinstance(note, Note):
        if note > 127 or note < 0:
            raise ValueError(f"MIDI does not support note {note}")
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
    """Return either an integer or a list
    of notes that represents note(s) in
    :arg:`name`.
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


"""Names of notes.
"""
NOTE_NAMES: list[str] = [
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
]


NOTES_MIDI: list[str] = [note_m2s(i) for i in range(0, 127 + 1)]


NOTES_CLASS: list[str] = NOTE_NAMES


NOTES = NOTES_MIDI

"""Map of each apartness to a name. The entry
`apartness`: (`major/minor`, `number`) means
apartness `apartness` is the `major/minor` `number`
:sup:`th`.
"""
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

INTERVALS: dict[str, int] = dict()
INTERVALS["prime 1"] = 0
INTERVALS["augmented 1"] = 1
INTERVALS["diminished 1"] = 11
for interval_semitone, (name, order) in interval_seeds.items():
    if name == "major":
        # from each major, produce: augmented +1, minor -1, diminished -2
        INTERVALS[f"augmented {order}"] =\
            (interval_semitone + 1) % len(NOTE_NAMES)
        INTERVALS[f"major {order}"] =\
            interval_semitone
        INTERVALS[f"minor {order}"] =\
            (interval_semitone - 1) % len(NOTE_NAMES)
        # Diminishing a minor gives -2 from major
        INTERVALS[f"diminished {order}"] =\
            (interval_semitone - 2) % len(NOTE_NAMES)
    elif name == "perfect":
        INTERVALS[f"augmented {order}"] =\
            (interval_semitone + 1) % len(NOTE_NAMES)
        INTERVALS[f"perfect {order}"] =\
            (interval_semitone) % len(NOTE_NAMES)
        INTERVALS[f"diminished {order}"] =\
            (interval_semitone - 1) % len(NOTE_NAMES)
    else:
        raise KeyError()


def interval_s2i(name: str) -> int:
    return INTERVALS[name]


def interval_i2s(key_num: int) -> list[str]:
    """Map an apartness to the appropriate name
    according to :attr:`INTERVALS`.
    """
    return [
        name
        for name, interval_semitone in INTERVALS.items()
        if interval_semitone == key_num
    ]


def name_interval(note_from: str, note_to: str) -> str:
    """Map an apartness to the appropriate name
    according to :attr:`INTERVALS`.
    """

    interval_semitone = (note_s2i(note_to) - note_s2i(note_from)) \
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


def interval_from_scale(scale: list[str],
                        poses: tuple[int, int]) -> list[str]:
    print(note_s2i(scale[poses[1]]) - note_s2i(scale[poses[0]]))
    return interval_i2s(abs(note_s2i(scale[poses[1]])
                            - note_s2i(scale[poses[0]])))


@overload
def invert(arg: str) -> str:
    pass


@overload
def invert(arg: Note) -> Note:
    pass


def invert(arg: int | str) -> Note | Interval | str:
    """Invert an interval. Or a note.

    Works with both because taking the
    modular complement happens to have the
    same effect on both.
    """
    if isinstance(arg, Note) or isinstance(arg, Interval):
        return (len(NOTE_NAMES) - arg) % len(NOTES)
    else:
        return note_i2s((len(NOTE_NAMES) - note_s2i(arg))
                        % len(NOTES))


interval_i2s(invert(INTERVALS["major 7"]))


def reach(base_key: str, interval: str | int) -> str:
    """ "Reach up" from :arg:`base_key` by
    :arg:`interval`. :arg:`interval` can be
    either a number (e.g. 1) or a string
    (e.g. augmented 8).

    In the latter case, :arg:`interval` should be a
    key in :attr:`INTERVALS`.
    """
    apartness: int
    if isinstance(interval, str):
        apartness = INTERVALS[interval]
    else:
        apartness = interval

    return note_i2s((note_s2i(base_key) + apartness) % len(NOTES))


def match_out_numbers(expr: str) -> str:
    manah: Optional[re.Match] = re.match("((?![0-9]).)*", expr)

    if manah:
        return manah.group(0)
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

    if isinstance(a, str) and isinstance(b, str):
        return match_out_numbers(a) == match_out_numbers(b)
    else:

        a = [match_out_numbers(x) for x in a]
        b = [match_out_numbers(x) for x in b]

        return collections.Counter(a) == collections.Counter(b)

    # return [invert(triad[0]), *triad[1:]]
