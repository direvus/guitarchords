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
ROMAN_FRETS = (
        'I',
        'II',
        'III',
        'IV',
        'V',
        'VI',
        'VII',
        'VIII',
        'IX',
        'X',
        'XI',
        'XII',
        'XIII',
        'XIV',
        'XV',
        'XVI',
        'XVII',
        'XVIII',
        'XIX',
        'XX',
        'XXI',
        'XXII',
        'XXIII',
        'XXIV',
        )


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


def modify_style(elem, key, value):
    """Modify one key inside the style attribute of an SVG element."""
    text = str(elem.attrib['style']).strip()
    parts = [x.split(':', maxsplit=1) for x in text.split(';')]
    style = {x: y for x, y in parts}
    style[key] = value
    result = ';'.join([f'{k}:{v}' for k, v in style.items()])
    elem.attrib['style'] = result


def set_played_note(tree, string, fret, flats=False):
    string_note = STRING_NOTES[string - 1]
    note_index = NOTES.index(string_note) + fret
    note = get_note_name(note_index, flats)
    notelabel = find_element_by_id(tree, f'note{string}')
    notelabel[0].text = note
    return note


def generate_chord(tree, chord, lefthand=False, romanfrets=False):
    result = deepcopy(tree)
    parent_map = {c: p for p in result.iter() for c in p}
    title = find_element_by_id(result, 'title')
    name = chord.get('name', '').strip()
    title[0].text = name

    root, mode = get_scale(name)
    flats = False
    if root == 'F' or root in FLATS.values():
        flats = True

    strings = chord.get('strings', [])
    fretted = []
    finger_frets = {}
    finger_strings = {}
    min_fret = None
    max_fret = 0
    for i, value in enumerate(strings):
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
        fret = int(fret)
        fretted.append((num, finger, fret))
        if min_fret is None or fret < min_fret:
            min_fret = fret
        if fret > max_fret:
            max_fret = fret
        if finger in finger_frets:
            finger_frets[finger].append(fret)
        else:
            finger_frets[finger] = [fret]
        if finger in finger_strings:
            finger_strings[finger].append(num)
        else:
            finger_strings[finger] = [num]

    if not min_fret is None and max_fret - min_fret > 3:
        raise ValueError("Cannot draw a span greater than 4 frets, sorry.")

    fret_ys = []
    fret_shift = 0
    if max_fret > 4:
        fret_shift = min_fret - 1
    for fret in range(1, 5):
        fretlabel = find_element_by_id(result, f'fret{fret}')
        fret_ys.append(float(fretlabel.attrib['y']))
        if romanfrets:
            fretlabel[0].text = ROMAN_FRETS[fret + fret_shift - 1]
        else:
            fretlabel[0].text = str(fret + fret_shift)
        if fret == 1 and fret_shift > 0:
            modify_style(fretlabel[0], 'fill', '#101010')

    string_xs = []
    for i in range(len(strings)):
        s = find_element_by_id(result, f'string{i+1}')
        x = float(s.attrib['x']) + float(s.attrib['width']) / 2
        string_xs.append(x)

    barres = set()
    for finger, frets in finger_frets.items():
        if len(frets) < 2 or len(set(frets)) != 1:
            continue
        strings = finger_strings.get(finger, [])
        min_string = min(strings)
        max_string = max(strings)
        length = max_string - min_string + 1
        mark = find_element_by_id(result, f'barre{length}')
        if not mark:
            # fall back to just using regular finger markers
            continue
        barres.add(finger)
        parent = parent_map[mark]
        mark = deepcopy(mark)
        parent.append(mark)
        mark[1][0].text = finger
        rect = mark[0]
        x = float(rect.attrib['x'])
        y = float(rect.attrib['y'])

        left_string = min_string if lefthand else max_string
        tx = string_xs[left_string - 1] - 16 - x

        relative_fret = frets[0] - fret_shift
        ty = fret_ys[relative_fret - 1] - 16 - y

        mark.attrib['transform'] = f'translate({tx},{ty})'

    for string, finger, fret in fretted:
        set_played_note(result, string, fret, flats)
        if finger in barres:
            continue
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

        s = find_element_by_id(result, f'string{string}')
        x = float(s.attrib['x']) + float(s.attrib['width']) / 2

        relative_fret = fret - fret_shift
        y = fret_ys[relative_fret - 1]
        mark.attrib['transform'] = f'translate({x - cx},{y - cy})'

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
