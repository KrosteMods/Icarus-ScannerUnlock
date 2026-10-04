#!/usr/bin/env python3
"""Erzeugt src/data/rows.json: die Vorkommen-Zeilen des Spiels, unveraendert
ausser dem einen Feld.

WARUM ERZEUGT UND NICHT GEPFLEGT: diese Mod UEBERSCHREIBT eine Spielzeile.
Eine von Hand getippte Zeile wuerde dabei alles verlieren, was in der echten
Zeile steht und hier nicht abgeschrieben wurde — Knotenmaterialien,
Hervorhebung, Abbauzeit. Deshalb wird die Zeile aus den Spieldaten GELESEN,
genau ein Feld gesetzt und sonst nichts angefasst. Nach einem Icarus-Update
laeuft das Skript neu, und die Zeile stimmt wieder.

    python3 tools/erzeuge-zeilen.py <ordner-mit-spieltabellen> [Vorkommen,...]

Ohne Liste wird nur `Ruby` freigeschaltet.
"""
import json, pathlib, sys

TABELLE = "World-D_OreDeposit"
FELD = "ScannerBlacklist"
WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / "src/data/rows.json"
VORGABE = ["Ruby"]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ref = pathlib.Path(sys.argv[1])
    wunsch = (sys.argv[2].split(",") if len(sys.argv) > 2 else VORGABE)

    daten = json.loads((ref / f"{TABELLE}.json").read_text(encoding="utf-8"))
    spiel = {r["Name"]: r for r in daten["Rows"]}

    fehlt = [n for n in wunsch if n not in spiel]
    if fehlt:
        print(f"FEHLER: nicht in {TABELLE}: {', '.join(fehlt)}")
        print("Vorhanden:", ", ".join(sorted(spiel)))
        return 1

    zeilen = []
    for name in wunsch:
        roh = spiel[name]
        if not roh.get(FELD):
            print(f"HINWEIS: '{name}' stand gar nicht auf der Sperrliste — "
                  f"die Zeile aendert dann nichts.")
        zeile = dict(roh)
        zeile[FELD] = False
        zeilen.append(zeile)
        print(f"{name}: {FELD} {roh.get(FELD, False)} -> False "
              f"({len(roh)} Felder uebernommen)")

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(json.dumps({
        "_hinweis": [
            "ERZEUGT von tools/erzeuge-zeilen.py — nicht von Hand aendern.",
            "",
            "Jede Zeile ist die Spielzeile aus World/D_OreDeposit, Feld fuer Feld",
            "uebernommen, mit genau einer Abweichung: ScannerBlacklist steht auf",
            "false. Damit zeigt der Erz-Scanner des Spiels das Vorkommen so an wie",
            "Eisen oder Kupfer.",
            "",
            "Diese Mod UEBERSCHREIBT damit bewusst Spielzeilen. Das ist der ganze",
            "Zweck; tools/pruefe-zeilen.py haelt fest, dass sonst nichts abweicht.",
        ],
        TABELLE: zeilen,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{ZIEL.relative_to(WURZEL)}: {len(zeilen)} Zeile(n)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
