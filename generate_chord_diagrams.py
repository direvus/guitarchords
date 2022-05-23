#!/usr/bin/env python3
# vim coding:utf-8
import os
import sys
from argparse import ArgumentParser
from copy import deepcopy
from xml.etree import ElementTree

import yaml


DEFAULT_TEMPLATE = 'chord_base.svg'

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


def find_element_by_id(root, elem_id):
    return root.find(f".//*[@id='{elem_id}']")


def remove_element(elem, parent_map):
    parent = parent_map[elem]
    parent.remove(elem)


def remove_element_by_id(root, elem_id, parent_map):
    elem = find_element_by_id(root, elem_id)
    remove_element(elem, parent_map)


def generate_chord(tree, chord):
    result = deepcopy(tree)
    parent_map = {c: p for p in result.iter() for c in p}
    title = find_element_by_id(result, 'title')
    title[0].text = chord.get('name', '')

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

        if isinstance(value, (list, tuple)):
            finger, fret = value[:2]
            finger = str(finger).upper()
            if finger == 'T':
                mark = find_element_by_id(result, f'thumb')
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
            note_index = (NOTES.index(string_note) + fret) % 12
            note = NOTES[note_index]
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
        with open(args.chords_file, 'r') as fp:
            chords = yaml.safe_load(fp)
    main(tree, chords, args.output_dir)
