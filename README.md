

<p align="center">
<img src="./media/logo.png" width=400em>
<h1 align="center"> OMUSIC</h1>
</p>

A computerisation of Western music theory.

See [this Notebook file](music_theory.ipynb) for a tutorial of this library.

## Components

This library has the following modules:

| Module        | Components                                                   |
| ------------- | ------------------------------------------------------------ |
| omusic        | Definition of the music space; functions that operate on single notes; |
| omusic.modes  | Patterns of interval. Examples are `MAJOR`, `HARMONIC_MINOR` and `IONIAN`. |
| omusic.scale  | Functions that construct scales.                             |
| omusic.chord  | Functions that construct chords                              |
| omusic.guitar | Functions that map notes to a visual fret board.             |
| omusic.midi   | Functions that play notes. Compatible with `.scale` and `.chord`. Can also accept manually specified notes. |

## Installation

Install from PyPI:

```bash
pip install omusic
```

Install from source:

```bash
# move to the root directory
pip install .
```

