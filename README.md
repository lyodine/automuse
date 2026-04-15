

<p align="center">
<img src="./media/logo.png" width=400em>
<h1 align="center"> AutoMuse</h1>
</p>

A computerisation of Western music theory.

Please see [this Notebook file](introduction.ipynb) for a brief tutorial. See the table below for more tutorials.

## Components

This library has the following modules:

| Module         | Components                                                   | Turorial                                                  |
| -------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| automuse         | Definition of the music space; functions that operate on single notes; | [Link](./docs/source/guides/examples/introduction.ipynb)  |
| automuse.modes   | Patterns of interval. Examples are `MAJOR`, `HARMONIC_MINOR` and `IONIAN`. | &#x2013;                                                  |
| automuse.scale   | Functions that construct scales.                             | &#x2013;                                                  |
| automuse.chord   | Functions that construct chords                              | &#x2013;                                                  |
| automuse.guitar  | Functions that map notes to a visual fret board.             | [Link](./docs/source/guides/examples/guessguitarer.ipynb) |
| automuse.transforms    | Mathematical transforms | [Link](./docs/source/guides/examples/transforms.ipynb)          |
| automuse.midi    | Functions that play notes. Compatible with `.scale` and `.chord`. Can also accept manually specified notes. | [Link](./docs/source/guides/examples/midi.ipynb)          |
| automuse.guesser | Function to guess a scale or a chord based on a set off notes. | [Link](./docs/source/guides/examples/guesser.ipynb)       |

## Installation

Install from PyPI:

```bash
pip install automuse
```

Install from source:

```bash
# move to the root directory
pip install .
```

