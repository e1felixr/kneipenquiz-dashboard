"""Kneipenquiz-Startpunkt.

Minimaler Bootstrap: er instanziert das Hauptfenster und startet die
Tk-Schleife. Reiter-Wahl und Logik liegen in quiz_eingabe.py.
"""
from quiz_eingabe import QuizEingabeApp


if __name__ == "__main__":
    QuizEingabeApp().mainloop()
