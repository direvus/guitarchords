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
const TUNING = ["E", "B", "G", "D", "A", "E"];

function mod_note(note, semitones) {
    i = NOTES.indexOf(note);
    if (i < 0) {
        throw "Invalid note name";
    }
    i = (i + semitones) % 12;
    return NOTES[i];
}

function show_played_note(string, fret) {
    if (fret == "X") {
        note = "-";
    } else {
        note = TUNING[string - 1];
        if (fret != "O") {
            note = mod_note(note, parseInt(fret));
        }
    }
    $("#played" + string.toString()).text(note);
}

function update_finger_disabled(string, fret) {
    vis = (fret == "X" || fret == "O");
    el = $("select[name='f" + string.toString() + "']");
    el.prop("disabled", vis);
    if (vis) {
        el.addClass("disabled");
    } else {
        el.removeClass("disabled");
    }
}

function update_string(string) {
    v = $("select[name='s" + string.toString() + "'] option:checked").val();
    show_played_note(string, v);
    update_finger_disabled(string, v);
}

function update_all_strings() {
    for (var i = 1; i <= 6; i++) {
        update_string(i);
    }
}

$(document).ready(update_all_strings);
