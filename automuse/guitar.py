"""Utilities that visualise notes on
a fretboard.
"""
from typing import Optional, Sequence
from . import note_s2i, NOTE_NAMES, NOTES, Note, note_i2s
import matplotlib.pyplot as plt

DEFAULT_TUNING: list[int] = note_s2i(["E", "B", "G", "D", "A", "E"])


# A way to (quasi-) intelligently guess if the
#   music space uses for octaves.
if NOTES != NOTE_NAMES:
    DEFAULT_TUNING = note_s2i(["E4", "A4", "D5", "G5", "B6", "E6"])
else:
    DEFAULT_TUNING = note_s2i(["E", "B", "G", "D", "A", "E"])


def notes_on_string(start: Note,
                    capo: int,
                    length: int) -> list[Note]:
    """Return a list of :arg:`length` notes on a
    string that begins with the :arg:`start` :sup:`th`
    note at capo :arg:`capo`.
    """
    return list[int]([(start + capo + i) % len(NOTES) for i in range(length)])


def notes_on_fretboard(capo: Note,
                       length: int,
                       tuning: list[Note]) -> list[list[Note]]:
    """Return a matrix of notes for all strings
    on a guitar for the given :arg:`tuning`.

    The item at [i][j] is the j\\ :sup:`th` note
    on the i\\ :sup:`th` string ... I think.
    """
    return [notes_on_string(key, capo, length)
            for key in tuning]


def notes_of_interest(
    notes: list[str], octave_matrix: list[list[int]], strict: bool = False
) -> list[list[Optional[int]]]:
    """Given a matrix of notes, replace
    items that are not in the given scale with
    None, then return the result.

    Use to visualise chords.
    """

    scale: Sequence[int] = note_s2i(notes)
    easy_scale: list[int] = [x % 12 for x in scale]

    def is_note_on_scale(note: int, strict: bool) -> bool:
        if strict:
            return note in scale
        else:
            return note % 12 in easy_scale

    return [
        [key if is_note_on_scale(key, strict) else None for key in string]
        for string in octave_matrix
    ]

    # Commented out code compare strictly,
    # notes_i: list[int] = note_s2i(notes)
    # return [
    #     [key if key in notes_i else None for key in string]\
    #         for string in octave_matrix
    # ]


FRET_OFFSET = 0.7


def disseminate_neural_lattices(height: int, length: int):
    """Render the local neighbourhood structure of
     a Riemannian topological manifold."""
    plt.gca().axis("off")

    for h in range(height + 1):
        plt.plot((0, length), (h, h), linewidth=0.7, color="black")

    for w in range(length):
        current_x = FRET_OFFSET + w
        plt.plot((current_x, current_x),
                 (0, height),
                 linewidth=1.5,
                 color="black")


X_KERN = 0.191
Y_KERN = -0.2


def draw_key_at_location(reverse_string_loc: int,
                         fret_loc: int,
                         key_name: str):
    plt.text(
        (fret_loc) + X_KERN,
        (reverse_string_loc) + Y_KERN,
        key_name,
        fontdict={"family": "PT Mono", "size": 19},
        horizontalalignment="center",
    ).set_bbox(
        dict(facecolor="white", alpha=1, edgecolor="white")
    )  # #D1D1D1


def draw_dot_at_location(reverse_string_loc: float, fret_loc: float, **kwargs):
    plt.scatter(
        (fret_loc) + X_KERN,
        (reverse_string_loc) + Y_KERN,
        color="black",
        **kwargs
    )


def draw_capo(capo: int) -> None:
    if capo > 0:
        plt.text(
            0,
            -2,
            f"capo: {capo}",
            fontdict={"family": "PT Mono", "size": 19},
            horizontalalignment="left",
        )
    elif capo == 0:
        plt.text(
            0,
            -2,
            f"capo: {0}",
            fontdict={"family": "PT Mono", "size": 19},
            horizontalalignment="left",
        )

    else:
        raise ValueError()


def draw_scale(
    scale: list[str], capo: int, width: int, strict: bool = False
) -> None:
    octave_matrix = notes_on_fretboard(capo, width, DEFAULT_TUNING)

    view_height = len(octave_matrix) - 1
    view_width = len(octave_matrix[0])

    octave_matrix_mask = notes_of_interest(scale, octave_matrix, strict)

    plt.figure(figsize=(view_width, view_height * 0.68))

    disseminate_neural_lattices(view_height, view_width)

    # In a typical visualisation of the fretboard, the top string
    #   ("high E") has the smallest index of 1. On the other hand,
    #   a smaller Y value is closer to the bottom.
    # Enumerating strings in the reverse order means, for example,
    #   the 6th string ("low E") is plotted first at the bottom-
    #   most position.
    for reverse_string_index, string in enumerate(
            reversed(octave_matrix_mask[::-1])):
        for fret_index, key in enumerate(string):
            if key is not None:
                draw_key_at_location(reverse_string_index,
                                     fret_index,
                                     note_i2s(key))

    note_locations: list[int] = [3, 5, 7, 9, 12, 15, 17]
    notable_frets: list[int] = [
        x - capo for x in note_locations if x >= 0 and x - capo < capo + width
    ]

    for x in notable_frets:
        draw_dot_at_location(reverse_string_loc=-0.6,
                             fret_loc=x)
        draw_dot_at_location(reverse_string_loc=2.7,
                             fret_loc=x,
                             s=60,
                             zorder=4)

    if 12 - capo in notable_frets:
        draw_dot_at_location(reverse_string_loc=-1,
                             fret_loc=12 - capo)

    if capo == 0:
        draw_dot_at_location(
            reverse_string_loc=-0.1,
            fret_loc=0.5 - capo,
            s=39,
            marker="^"
        )

        draw_dot_at_location(
            reverse_string_loc=5.5, fret_loc=0.5 - capo, s=39, marker="v"
        )
        plt.plot((FRET_OFFSET, FRET_OFFSET),
                 (0, 5),
                 linewidth=3,
                 color="black")


# disseminate_neural_lattices(6, 5)

# print(*[note_i2s(x) for x in notes_on_fretboard(0,
# 12, DEFAULT_TUNING)], sep="\n")
