const NOTES = [
        "A",
        "A♯",
        "B",
        "C",
        "C♯",
        "D",
        "D♯",
        "E",
        "F",
        "F♯",
        "G",
        "G♯"
        ];
const FLATS = {
        "B♭": "A♯",
        "D♭": "C♯",
        "E♭": "D♯",
        "G♭": "F♯",
        "A♭": "G♯"
        };
const TUNING = ["E", "B", "G", "D", "A", "E"];
const SCALES = {
        "major": {
            0: "I",
            2: "ii",
            4: "iii",
            5: "IV",
            7: "V",
            9: "vi",
            11: "vii"
            },
        "minor": {
            0: "i",
            2: "ii",
            3: "III",
            5: "iv",
            7: "v",
            8: "VI",
            10: "VII"
            }
        };

function get_string_note(string, fret) {
    if (fret == "X") {
        return "-";
    }
    var note = TUNING[string - 1];
    if (fret != "O") {
        note = mod_note(note, parseInt(fret));
    }
    return note;
}

function mod_note(note, semitones) {
    var i = NOTES.indexOf(note);
    if (i < 0) {
        throw "Invalid note name";
    }
    i = (i + semitones) % 12;
    return NOTES[i];
}

function get_scale_degree(root, mode, note) {
    if (!(mode in SCALES)) {
        return null;
    }
    i = NOTES.indexOf(root);
    j = NOTES.indexOf(note);
    diff = (j - i) % 12;
    if (diff < 0) {
        diff += 12;
    }
    scale = SCALES[mode];
    if (!(diff in scale)) {
        return null;
    }
    return scale[diff];
}

function show_played_note(string, note) {
    $("#played" + string.toString()).text(note);
}

function show_scale_degree(root, mode, string, note) {
    var degree = get_scale_degree(root, mode, note);
    $("#degree" + string.toString()).text(degree);
}

function update_finger_disabled(string, fret) {
    var vis = (fret == "X" || fret == "O");
    var el = $("select[name='f" + string.toString() + "']");
    el.prop("disabled", vis);
    if (vis) {
        el.addClass("disabled");
    } else {
        el.removeClass("disabled");
    }
}

function update_string(root, mode, string) {
    fret = $("select[name='s" + string.toString() + "'] option:checked").val();
    note = get_string_note(string, fret);
    show_played_note(string, note);
    show_scale_degree(root, mode, string, note);
    update_finger_disabled(string, fret);
}

function get_scale() {
    var name = $("input[name='name']").val().trim();
    var name = name.replaceAll(/\s+/g, '');
    var matches = name.match(/^([A-Ga-g])([#♯b♭])?(.*)/);
    if (matches == null) {
        return null;
    }
    if (matches[2] == "#") {
        matches[2] = "♯";
    } else if (matches[2] == "b") {
        matches[2] = "♭";
    }
    var root = matches[1].toUpperCase();
    if (matches[2]) {
        root += matches[2];
    }
    if (root in FLATS) {
        root = FLATS[root];
    }
    var mode = "major";
    if (matches[3].match(/^m/) && !matches[3].match(/^m[aj]/)) {
        mode = "minor";
    }
    return [root, mode];
}

function update_one_string(string) {
    scale = get_scale();
    update_string(scale[0], scale[1], i);
}

function update_all_strings() {
    var scale = get_scale();
    for (var i = 1; i <= 6; i++) {
        update_string(scale[0], scale[1], i);
        console.log(scale, i);
    }
}

$(document).ready(update_all_strings);
