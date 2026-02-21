from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import random

app = Flask(__name__)
# nötig für session (später sicher machen!)
app.secret_key = "dev-secret-change-me"


def lade_fragen():
    # lädt fragen.json aus dem gleichen Ordner wie app.py
    pfad = os.path.join(os.path.dirname(__file__), "fragen.json")
    with open(pfad, "r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/")
def start():
    # Neue Quiz-Runde initialisieren
    fragen = lade_fragen()
    random.shuffle(fragen)

    # ganze Fragenliste in session (für kleine Demo ok)
    session["fragen"] = fragen
    session["index"] = 0
    session["punkte"] = 0
    session["feedback"] = None

    return redirect(url_for("quiz"))


@app.get("/quiz")
def quiz():
    fragen = session.get("fragen")
    if not fragen:
        return redirect(url_for("start"))

    idx = session.get("index", 0)
    if idx >= len(fragen):
        return redirect(url_for("result"))

    frage = fragen[idx]
    feedback = session.get("feedback")
    session["feedback"] = None  # Feedback nur einmal anzeigen

    return render_template(
        "quiz.html",
        frage=frage,
        idx=idx,
        total=len(fragen),
        punkte=session.get("punkte", 0),
        feedback=feedback
    )


@app.post("/answer")
def answer():
    fragen = session.get("fragen")
    if not fragen:
        return redirect(url_for("start"))

    idx = session.get("index", 0)
    frage = fragen[idx]

    antwort = request.form.get("antwort", "").lower().strip()
    gueltig = antwort in ["a", "b", "c", "d"]

    if not gueltig:
        session["feedback"] = ("Bitte nur a, b, c oder d auswählen.", False)
        return redirect(url_for("quiz"))

    richtig = (antwort == frage["richtig"])
    if richtig:
        session["punkte"] = session.get("punkte", 0) + 1
        session["feedback"] = ("Richtig! 🎉", True)
    else:
        richtiger_text = frage["optionen"][frage["richtig"]]
        session["feedback"] = (
            f"Falsch 😬 (richtig wäre: {richtiger_text})", False)

    # zur nächsten Frage
    session["index"] = idx + 1
    return redirect(url_for("quiz"))


@app.get("/result")
def result():
    fragen = session.get("fragen") or []
    return render_template(
        "result.html",
        punkte=session.get("punkte", 0),
        total=len(fragen)
    )


if __name__ == "__main__":
    app.run(debug=True)
