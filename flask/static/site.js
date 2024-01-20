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
        "1":  "B♭",
        "4":  "D♭",
        "6":  "E♭",
        "9":  "G♭",
        "11": "A♭",
        };
const TUNING = ["E", "B", "G", "D", "A", "E"];
const SCALES = {
        "major": {
            0: "1",
            1: "♭2",
            2: "2",
            3: "♭3",
            4: "3",
            5: "4",
            6: "♭5",
            7: "5",
            8: "♭6",
            9: "6",
            10: "♭7",
            11: "7"
            },
        "minor": {
            0: "1",
            1: "♭2",
            2: "2",
            3: "3",
            4: "♭4",
            5: "4",
            6: "♭5",
            7: "5",
            8: "6",
            9: "♭7",
            10: "7",
            11: "♯7"
            }
        };

function get_string_note(string, fret) {
    if (fret == "X") {
        return null;
    }
    var note = TUNING[string - 1];
    var i = NOTES.indexOf(note);
    if (fret != "O") {
        i = (i + parseInt(fret)) % 12;
    }
    return i;
}

function get_note_name(index, flats) {
    if (index === null) {
        return null;
    }
    index = index % 12;
    if (flats && index in FLATS) {
        return FLATS[index];
    }
    return NOTES[index];
}

function get_scale_degree(root, mode, note) {
    if (!(mode in SCALES)) {
        return null;
    }
    var diff = (note - root) % 12;
    if (diff < 0) {
        diff += 12;
    }
    var scale = SCALES[mode];
    if (!(diff in scale)) {
        return null;
    }
    return scale[diff];
}

function show_played_note(string, note) {
    var text = note;
    if (note === null) {
        text = "-";
    }
    $("#played" + string.toString()).text(text);
}

function show_scale_degree(root_index, mode, string, note_index) {
    var degree = "";
    if (root_index !== null && mode !== null && note_index !== null) {
        degree = get_scale_degree(root_index, mode, note_index);
    }
    $("#degree" + string.toString()).text(degree);
}

function update_finger_input(string, fret) {
    var disable = (fret == "X" || fret == "O");
    var el = $("select[name='f" + string.toString() + "']");
    el.prop("disabled", disable);
    if (disable) {
        el.addClass("disabled");
        return true;
    }
    el.removeClass("disabled");
    var val = el[0].value;
    var valid = (val != "");

    if (valid) {
        el.removeClass("error");
    } else {
        el.addClass("error");
    }
    return valid;
}

function update_string(root, mode, string) {
    var fret = $("select[name='s" + string.toString() + "'] option:checked").val();
    var flats = false;
    var root_index = NOTES.indexOf(root);
    if (root[1] == "♭") {
        flats = true;
        root_index = NOTES.indexOf(root[0]) - 1;
        if (root_index < 0) {
            root_index += 12;
        }
    } else if (root == "F") {
        flats = true;
    }
    var index = get_string_note(string, fret);
    var name = get_note_name(index, flats);
    show_played_note(string, name);
    show_scale_degree(root_index, mode, string, index);
    return update_finger_input(string, fret);
}

function update_submit_button(valid) {
    var el = $("button[type='submit']");
    el.prop("disabled", !valid);
    if (valid) {
        el.removeClass("disabled");
    } else {
        el.addClass("disabled");
    }
}

function get_scale() {
    var name = $("input[name='name']").val().trim();
    var name = name.replaceAll(/\s+/g, '');
    var matches = name.match(/^([A-Ga-g])([#♯b♭])?(.*)/);
    if (matches == null) {
        return [null, null];
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
    var mode = "major";
    if (matches[3].match(/^m/) && !matches[3].match(/^m[aj]/)) {
        mode = "minor";
    }
    return [root, mode];
}

function update_one_string(string) {
    scale = get_scale();
    update_string(scale[0], scale[1], string);
}

function update_all_strings() {
    var name = $("input[name='name']").val().trim();
    var scale = get_scale();
    var valid = true;
    if (name != "" && scale[0] === null) {
        $("#scale-warning").removeClass("hidden");
    }
    var min_fret = 0;
    var max_fret = 0;
    for (var i = 1; i <= 6; i++) {
        var fret = parseInt($("select[name='s" + i.toString() + "'] option:checked").val());
        string_valid = update_string(scale[0], scale[1], i);
        if (!string_valid) {
            valid = false;
        }
        if (min_fret < 1 || fret < min_fret) {
            min_fret = fret;
        }
        if (fret > max_fret) {
            max_fret = fret;
        }
    }
    if (max_fret - min_fret > 3) {
        $("#span-error").removeClass("hidden");
        valid = false;
    } else {
        $("#span-error").addClass("hidden");
    }
    update_submit_button(valid);
}

$(document).ready(update_all_strings);
