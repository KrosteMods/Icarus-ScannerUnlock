#!/usr/bin/env python3
"""Prueft src/data/rows.json gegen die Spieltabellen.

Diese Mod ueberschreibt Spielzeilen. Der Fehler, der dabei nicht auffaellt:
ein Feld, das in der Spielzeile steht und in unserer fehlt — dann setzt die
Mod es auf den Tabellen-Default zurueck, und im Spiel verschwindet ein
Knotenmaterial oder eine Abbauzeit. Deshalb wird Feld fuer Feld verglichen.

    python3 tools/pruefe-zeilen.py <ordner-mit-spieltabellen>
"""
import json, pathlib, sys

FELD = "ScannerBlacklist"
WURZEL = pathlib.Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    ref = pathlib.Path(sys.argv[1])
    unser = json.loads((WURZEL / "src/data/rows.json").read_text(encoding="utf-8"))

    fehler, warnungen = 0, 0
    for tabelle, zeilen in unser.items():
        if tabelle.startswith("_"):
            continue
        pfad = ref / f"{tabelle}.json"
        if not pfad.exists():
            print(f"FEHLER: Spieltabelle fehlt: {pfad.name}")
            fehler += 1
            continue
        daten = json.loads(pfad.read_text(encoding="utf-8"))
        spiel = {r["Name"]: r for r in daten["Rows"]}
        for zeile in zeilen:
            name = zeile["Name"]
            if name not in spiel:
                print(f"FEHLER: {tabelle}.{name} gibt es im Spiel nicht")
                fehler += 1
                continue
            echt = spiel[name]
            # Erfundene Felder: im Spiel weder in der Zeile noch im Default.
            erlaubt = set(echt) | set(daten.get("Defaults", {}))
            for f in zeile:
                if f not in erlaubt:
                    print(f"FEHLER: {tabelle}.{name}: Feld '{f}' kennt das Spiel nicht")
                    fehler += 1
            # Verlorene Felder: in der Spielzeile, bei uns nicht.
            for f in echt:
                if f not in zeile:
                    print(f"FEHLER: {tabelle}.{name}: Feld '{f}' fehlt — die Mod wuerde "
                          f"es auf den Default zuruecksetzen")
                    fehler += 1
            # Genau eine gewollte Abweichung. Ein Feld, das es im Spiel nur
            # als Default gibt und das wir zusaetzlich setzen, zaehlt mit:
            # es aendert das Verhalten und faellt sonst durch, weil die
            # Feldnamenpruefung oben Default-Felder erlaubt.
            abweichungen = [f for f in echt if f in zeile and echt[f] != zeile[f]]
            abweichungen += [f for f in zeile if f not in echt]
            if abweichungen != [FELD]:
                print(f"FEHLER: {tabelle}.{name}: abweichende Felder {abweichungen}, "
                      f"erwartet genau ['{FELD}']")
                fehler += 1
            elif zeile[FELD] is not False:
                print(f"FEHLER: {tabelle}.{name}: {FELD} ist {zeile[FELD]}, erwartet False")
                fehler += 1
            else:
                print(f"ok    {tabelle}.{name}: {len(echt)} Felder gleich, "
                      f"{FELD} {echt[FELD]} -> False")
            # Verweise aufloesen, damit ein Spiel-Update nicht still bricht.
            #
            # Der Tabellenname steht in der Spielzeile meist NICHT dabei: er
            # kommt aus "Defaults". Ohne diesen Rueckgriff prueft die Schleife
            # gar nichts und meldet trotzdem "0 Fehler" — genau so stand es
            # hier im ersten Entwurf.
            vorgaben = daten.get("Defaults", {})
            for f, wert in zeile.items():
                if isinstance(wert, dict) and "RowName" in wert:
                    vorgabe = vorgaben.get(f) if isinstance(vorgaben.get(f), dict) else {}
                    zt = wert.get("DataTableName") or vorgabe.get("DataTableName")
                    rn = wert["RowName"]
                    if rn in ("None", None):
                        continue
                    if not zt:
                        print(f"WARNUNG: {name}.{f}: Verweis ohne Tabellenname, "
                              f"auch nicht im Default — nicht pruefbar")
                        warnungen += 1
                        continue
                    kandidaten = list(ref.glob(f"*-{zt}.json")) + list(ref.glob(f"{zt}.json"))
                    if not kandidaten:
                        print(f"WARNUNG: {name}.{f}: Tabelle {zt} nicht im Referenzordner")
                        warnungen += 1
                        continue
                    ziel = json.loads(kandidaten[0].read_text(encoding="utf-8"))
                    if rn not in {r["Name"] for r in ziel["Rows"]}:
                        print(f"FEHLER: {name}.{f}: '{rn}' gibt es in {zt} nicht")
                        fehler += 1

    print(f"\n{fehler} Fehler, {warnungen} Warnungen")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
