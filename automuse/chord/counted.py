"""Utilities that construct chords by counting intervals.
"""
from .. import reach, reach_many


def count_triad_major(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "major 3", "perfect 5"])


def count_triad_minor(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "minor 3", "perfect 5"])


def count_triad_augmented(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "major 3", "augmented 5"])


def count_triad_diminished(root: str) -> list[str]:
    return reach_many(root, ["prime 1", "minor 3", "diminished 5"])


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
