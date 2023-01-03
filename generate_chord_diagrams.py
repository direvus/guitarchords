#!/usr/bin/env python3
# vim coding:utf-8
import os
import re
import sys
from argparse import ArgumentParser
from copy import deepcopy
from xml.etree import ElementTree

import yaml


DEFAULT_TEMPLATE = 'chord_base.svg'
WHITESPACE_RE = re.compile(r'\s+')
ROOT_RE = re.compile(r'^([A-Ga-g])([#♯b♭])?(.*)')
NOTES = [
        'A',
        'A♯',
        'B',
        'C',
        'C♯',
        'D',
        'D♯',
        'E',
        'F',
        'F♯',
        'G',
        'G♯',
        ]
STRING_NOTES = [
        'E',
        'B',
        'G',
        'D',
        'A',
        'E',
        ]
FLATS = {
        1:  'B♭',
        4:  'D♭',
        6:  'E♭',
        9:  'G♭',
        11: 'A♭',
        }


def find_element_by_id(root, elem_id):
    return root.find(f".//*[@id='{elem_id}']")


def remove_element(elem, parent_map):
    parent = parent_map[elem]
    parent.remove(elem)


def remove_element_by_id(root, elem_id, parent_map):
    elem = find_element_by_id(root, elem_id)
    remove_element(elem, parent_map)


def get_note_name(index, flats=False):
    index = index % 12
    if flats and index in FLATS:
        return FLATS[index]
    return NOTES[index]


def get_scale(name):
    """Get the scale from a chord name.

    Returns a tuple containing the root note name, followed by the mode
    ('major' or 'minor') in lowercase.

    For sharp or flat root note names, a '#' or 'b' in the chord name will be
    translated into the actual sharp or flat symbol respectively.

    For example:
        get_scale('Am7') -> ('A', 'minor')
        get_scale('Bb') -> ('B♭', 'major')

    Return (None, None) if the chord name fails to parse.
    """
    name = WHITESPACE_RE.sub('', str(name))
    if not name:
        return (None, None)
    match = ROOT_RE.match(name)
    if match is None:
        return (None, None)
    root = match.group(1).upper()
    mode = 'major'

    if match.group(2):
        acc = match.group(2)
        if acc == '#':
            acc = '♯'
        elif acc == 'b':
            acc = '♭'
        root += acc

    if match.group(3):
        rem = match.group(3).lower()
        if rem[0] == 'm' and (len(rem) == 1 or rem[1] not in {'a', 'j'}):
            mode = 'minor'

    return [root, mode]


def generate_chord(tree, chord):
    result = deepcopy(tree)
    parent_map = {c: p for p in result.iter() for c in p}
    title = find_element_by_id(result, 'title')
    name = chord.get('name', '').strip()
    title[0].text = name

    root, mode = get_scale(name)
    flats = False
    if root == 'F' or root in FLATS.values():
        flats = True

    for i, value in enumerate(chord.get('strings', [])):
        num = i + 1
        if isinstance(value, (str, int)):
            value = str(value).upper()

        if value in ('X', 'M'):
            remove_element_by_id(result, f'note{num}', parent_map)
        else:
            remove_element_by_id(result, f'mute{num}', parent_map)

        if value not in ('O', '0'):
            remove_element_by_id(result, f'open{num}', parent_map)

        if not isinstance(value, (list, tuple)):
            continue

        finger, fret = value[:2]
        finger = str(finger).upper()
        if finger == 'T':
            mark = find_element_by_id(result, 'thumb')
        else:
            mark = find_element_by_id(result, f'finger{finger}')
        parent = parent_map[mark]
        mark = deepcopy(mark)
        parent.append(mark)
        circle = mark[0]
        cx = float(circle.attrib['cx'])
        cy = float(circle.attrib['cy'])

        s = find_element_by_id(result, f'string{num}')
        x = float(s.attrib['x']) + float(s.attrib['width']) / 2

        fretlabel = find_element_by_id(result, f'fret{fret}')
        y = float(fretlabel.attrib['y'])
        mark.attrib['transform'] = f'translate({x - cx}, {y - cy})'

        string_note = STRING_NOTES[i]
        note_index = NOTES.index(string_note) + fret
        note = get_note_name(note_index, flats)
        notelabel = find_element_by_id(result, f'note{num}')
        notelabel[0].text = note

    return result


def main(tree, chords, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for chord in chords:
        diag = generate_chord(tree, chord)
        name = chord['name'].replace('/', '_').replace(' ', '_')
        filename = os.path.join(output_dir, f"{name}.svg")
        diag.write(filename)
        print(f"Generated {filename}")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-d', '--output-dir', default='build')
    parser.add_argument('-t', '--template-file', default=DEFAULT_TEMPLATE)
    parser.add_argument('-f', '--chords-file', default='-')
    args = parser.parse_args()

    tree = ElementTree.parse(args.template_file)
    if args.chords_file == '-':
        chords = yaml.safe_load(sys.stdin)
    else:
        with open(args.chords_file, 'r', encoding='utf-8') as fp:
            chords = yaml.safe_load(fp)
    main(tree, chords, args.output_dir)
