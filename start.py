"""Kneipenquiz-Startpunkt.

Minimaler Bootstrap: er instanziert das Hauptfenster und startet die
Tk-Schleife. Reiter-Wahl und Logik liegen in quiz_eingabe.py.
"""
import warnings

# Verfalls-/Zukunfts-Warnungen aus der Konsole fernhalten, sofern sie durch
# UNSEREN Code ausgelöst werden. pandas & Co. schreiben solche Warnungen per
# stacklevel dem aufrufenden Modul zu, nicht sich selbst; daher greift der
# Modul-Filter auf die eigenen Module, nicht auf "pandas". Warnungen aus fremden
# Codepfaden bleiben bewusst sichtbar.
for _warn_cat in (FutureWarning, DeprecationWarning, PendingDeprecationWarning):
    warnings.filterwarnings(
        "ignore", category=_warn_cat, module=r"(quiz_eingabe)(\.|$)"
    )

from quiz_eingabe import QuizEingabeApp


if __name__ == "__main__":
    QuizEingabeApp().mainloop()
