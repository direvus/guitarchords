# guitarchords
Generator for guitar chord diagrams

![Example of diagram for Cadd9 chord](/doc/Cadd9.png)

This is a program that generates a suite of guitar chord diagrams.

It uses an SVG template and a list of chord definitions in YAML, and produces
one diagram for each of the chords defined.

The repository comes with a default template and chord definition list, but you
are free to modify the template and/or the chords, or create your own from
scratch.

## Usage

```
generate_chord_diagrams.py [-t TEMPLATE_FILE] [-f CHORDS_FILE] [-d OUTPUT_DIR]
```

By default, `generate_chord_diagrams.py` will expect to find an SVG template
file named `chord_base.svg` in the current directory, and to receive a YAML
chord definition document on standard input.  It will write out the generated
chord diagrams as SVG to a directory named `build/`.  All of these defaults can
be overridden with command-line arguments.

## Dependencies

- Python 3
- [pyyaml](https://pyyaml.org) pip package
- Inkscape or similar, if you want to export the diagrams to raster format

## Installation

Copy `generate_chord_diagrams.py` (and optionally `chord_base.svg` and
`chords.yaml`) to your computer.

## Chord definition format

Chords are defined as objects with two required properties:

- name
- strings

The `string` property must be a list of strings from highest pitch to lowest
pitch.  Each string should be one of the following values:

- An open string, indicated by uppercase letter `O`
- A muted string, indicated by uppercase letter `X`
- A fretted string, indicated by a 2-element list of the finger number,
  followed by the fret number.

Fingers are numbered from the index finger as 1, to the little finger as 4.
The thumb is indicated with uppercase letter `T`.

For example, the Cadd9 chord defined in YAML is:

```yaml
- name: Cadd9
  strings:
    - [4, 3]
    - [3, 3]
    - O
    - [1, 2]
    - [2, 3]
    - X
```

This has the meaning:

- The first string (the high E string) is fretted with the fourth
  finger on the third fret.
- The second string (B) is fretted with the third finger on the third fret.
- The third string (G) is played open.
- The fourth string (D) is fretted with the first finger on the second fret.
- The fifth string (A) is fretted with the second finger on the third fret.
- The sixth string (low E) is muted.

## Credits

Written by [Brendan Jurd](mailto:direvus@gmail.com)
