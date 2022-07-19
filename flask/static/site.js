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

function show_played_note(string) {
    v = $("select[name='s" + string.toString() + "'] option:checked").val();
    if (v == "X") {
        note = "-";
    } else {
        note = TUNING[string - 1];
        if (v != "O") {
            note = mod_note(note, parseInt(v));
        }
    }
    console.log(note);
    $("#played" + string.toString()).text(note);
}

function show_all_played_notes() {
    for (var i = 1; i <= 6; i++) {
        show_played_note(i);
    }
}

$(document).ready(show_all_played_notes);
