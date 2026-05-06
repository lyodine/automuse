

<p align="center">
<img src="http://yidingli.com/media/automuse_logo.png" width=400em>
<h1 align="center"> AutoMuse</h1>
</p>

A computerisation of Western music theory.

Please see [this Notebook file](http://yidingli.com/docs/automuse/guides/examples/introduction.html) for a brief tutorial. See the following table.

## Components

This library has the following modules:

| Module         | Components                                                   | Tutorial                                                  |
| -------------- | ------------------------------------------------------------ | --------------------------------------------------------- |
| automuse         | Definition of the music space; functions that operate on single notes; | [Link](http://yidingli.com/docs/automuse/guides/examples/introduction.html)  |
| automuse.modes   | Patterns of interval. Examples are `MAJOR`, `HARMONIC_MINOR` and `IONIAN`. | &#x2013;                                                  |
| automuse.scale   | Functions that construct scales.                             | &#x2013;                                                  |
| automuse.chord   | Functions that construct chords                              | &#x2013;                                                  |
| automuse.guitar  | Functions that map notes to a visual fret board.             | [Link](http://yidingli.com/docs/automuse/guides/examples/guitar.html) |
| automuse.transforms    | Mathematical transforms | [Link](http://yidingli.com/docs/automuse/guides/examples/transforms.html)          |
| automuse.midi    | Functions that play notes. Compatible with `.scale` and `.chord`. Can also accept manually specified notes. | [Link](http://yidingli.com/docs/automuse/guides/examples/midi.html)          |
| automuse.guesser | Function to guess a scale or a chord based on a set off notes. | [Link](http://yidingli.com/docs/automuse/guides/examples/guesser.html)       |

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

