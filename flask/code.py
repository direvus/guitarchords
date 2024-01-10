#!/usr/bin/env python
import os
import re
import subprocess
from copy import deepcopy
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree

import yaml
from flask import Flask, request, render_template, send_file
from generate_chord_diagrams import generate_chord


prefix = '/guitarchords'
app = Flask(__name__)
urls = (
        '/', 'index',
        prefix, 'index',
        prefix + '/', 'index',
        )


def strings_to_long_form(chord):
    """Convert a chord's string definition into long form.

    This means that every string will be a list of 2 elements, the fretting
    followed by the finger, even for strings that are open or muted.
    """
    strings = []
    for string in chord['strings']:
        if isinstance(string, str):
            strings.append(['', string])
        else:
            strings.append(string)
    result = deepcopy(chord)
    result['strings'] = strings
    return result


def strings_to_short_form(chord):
    """Convert a chord's string definition into short form.

    This means that only fretted strings will be a list of 2 elements, open or
    muted strings will be a single-character string 'O' or 'X'.
    """
    strings = []
    for finger, fret in chord['strings']:
        if fret in {'X', 'O'}:
            strings.append(fret)
        else:
            strings.append([finger, fret])
    result = deepcopy(chord)
    result['strings'] = strings
    return result


def validate_chord(request):
    name = request.args.get('name', '').strip()
    strings = []
    for n in range(1, 7):
        fret = request.args.get(f's{n}', 'O').strip().upper()
        finger = request.args.get(f'f{n}', '').strip().upper()
        if fret in {'M', 'X'}:
            fret = 'X'
        elif finger and fret.isdigit():
            fret = int(fret)
            if finger.isdigit():
                finger = int(finger)
        strings.append([finger, fret])
    return {
            'name': name,
            'strings': strings,
            }


def validate_bool(value):
    return value.strip() == '1'


def validate_left_handed(request):
    return validate_bool(request.args.get('lh', ''))


def validate_roman_frets(request):
    return validate_bool(request.args.get('rf', ''))


def get_inkscape_version(command='inkscape'):
    """Return the version of Inkscape, as a tuple of 3 integers."""
    proc = subprocess.run([command, '-V'], capture_output=True, check=True)
    out = proc.stdout.decode('utf-8')
    match = re.match(r'^Inkscape (\d+)\.(\d+)\.(\d+)', out)
    if not match:
        raise Exception("Failed to parse output from Inkscape version string.")
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)))


def generate_diagram(chord, left=False, romanfrets=False, width=209):
    template_file = 'chord_base.svg'
    if left:
        template_file = 'chord_base_lh.svg'
    tree = ElementTree.parse(template_file)
    diag = generate_chord(tree, chord, left, romanfrets)
    svgfile = NamedTemporaryFile(suffix='.svg', delete=False)
    diag.write(svgfile)
    svgfile.close()
    pngfile = NamedTemporaryFile(suffix='.png', delete=False)
    pngfile.close()

    ver = get_inkscape_version()
    args = ['inkscape', '-C', '-w', str(width)]
    if ver[0] < 1:
        args.extend(['-z', '-e', pngfile.name])
    else:
        args.extend(['--export-type=png', '-o', pngfile.name])
    args.append(svgfile.name)
    subprocess.run(args, check=True)
    os.remove(svgfile.name)
    return pngfile.name


@app.route('/')
def index():
    with open('chords.yaml', 'r', encoding='utf-8') as fp:
        presets = yaml.safe_load(fp)
    initials = []
    groups = {}
    for chord in presets:
        chord = strings_to_long_form(chord)
        initial = chord['name'][0].upper()
        if initial in groups:
            groups[initial].append(chord)
        else:
            groups[initial] = [chord]
            initials.append(initial)

    presets = [(x, groups[x]) for x in initials]
    chord = validate_chord(request)
    left = validate_left_handed(request)
    romanfrets = validate_roman_frets(request)
    return render_template(
            'index.html',
            name=chord['name'],
            left=left,
            romanfrets=romanfrets,
            strings=chord['strings'],
            presets=presets,
            )


@app.route('/chord')
def chord():
    left = validate_left_handed(request)
    romanfrets = validate_roman_frets(request)
    chord = validate_chord(request)
    chord = strings_to_short_form(chord)
    filename = generate_diagram(chord, left, romanfrets)
    result = send_file(filename, 'image/png')
    os.remove(filename)
    return result


@app.route('/download')
def download():
    left = validate_left_handed(request)
    romanfrets = validate_roman_frets(request)
    chord = validate_chord(request)
    chord = strings_to_short_form(chord)
    filename = generate_diagram(chord, left, romanfrets)
    basename = re.sub(r'[\W]+', '', chord['name'])
    if left:
        basename += '_lh'
    dlname = basename + '.png'
    result = send_file(
            filename,
            'image/png',
            as_attachment=True,
            attachment_filename=dlname)
    os.remove(filename)
    return result
