#!/usr/bin/env python3
"""Prueft src/data/rows.json gegen die Spieltabellen.

Diese Mod ueberschreibt Spielzeilen. Der Fehler, der dabei nicht auffaellt:
ein Feld, das in der Spielzeile steht und in unserer fehlt — dann setzt die
Mod es auf den Tabellen-Default zurueck, und im Spiel verschwindet ein
Knotenmaterial oder eine Abbauzeit. Deshalb wird Feld fuer Feld verglichen.

Dazu die Namenskette: ein freigeschaltetes Vorkommen braucht einen anzeigbaren
Namen, sonst steht im Scanner eine LEERE Zeile. Am 04.10.2026 im Spiel von
Lars gemeldet, Ursache war ein Loch in den Spieldaten: D_ItemTemplate.
Cobalt_Ore zeigt auf eine Zeile Cobalt_Ore in D_ItemsStatic, die es nicht
gibt. Seitdem wird die Kette hier geprueft, nicht im Spiel.

    python3 tools/pruefe-zeilen.py <ordner-mit-spieltabellen>
"""
import json, pathlib, sys

FELD = "ScannerBlacklist"
WURZEL = pathlib.Path(__file__).resolve().parent.parent


def lade(ref, tabelle):
    """Eine Spieltabelle als {Zeilenname: Zeile}, oder None."""
    treffer = list(ref.glob(f"*-{tabelle}.json")) + list(ref.glob(f"{tabelle}.json"))
    if not treffer:
        return None
    d = json.loads(treffer[0].read_text(encoding="utf-8"))
    return {r["Name"]: r for r in d["Rows"]}


def namenskette(ref, zeile):
    """Vom Vorkommen zum Anzeigenamen. Gibt (name, fehler) zurueck.

    Der Scanner braucht beides: die Hervorhebung benennt das Vorkommen, der
    Gegenstand benennt, was herauskommt. Reisst die Kette, bleibt das Feld im
    Scanner leer — ohne Fehlermeldung im Spiel.
    """
    fehler = []
    name = zeile["Name"]

    hl = lade(ref, "D_Highlightable")
    hr = (zeile.get("HighlightableRow") or {}).get("RowName")
    if not hr or hr == "None":
        fehler.append(f"{name}: keine HighlightableRow — der Scanner hat nichts zu benennen")
    elif hl is not None and not (hl.get(hr) or {}).get("DisplayName"):
        fehler.append(f"{name}: Hervorhebung '{hr}' hat keinen DisplayName")

    tmpl = lade(ref, "D_ItemTemplate")
    stat = lade(ref, "D_ItemsStatic")
    item = lade(ref, "D_Itemable")
    rt = (zeile.get("ResourceType") or {}).get("RowName")
    if not rt or rt == "None":
        fehler.append(f"{name}: kein ResourceType")
        return name, fehler
    if tmpl is None or stat is None or item is None:
        return name, fehler
    if rt not in tmpl:
        fehler.append(f"{name}: ResourceType '{rt}' gibt es in D_ItemTemplate nicht")
        return name, fehler
    sr = (tmpl[rt].get("ItemStaticData") or {}).get("RowName")
    if not sr or sr not in stat:
        fehler.append(f"{name}: D_ItemTemplate.{rt} zeigt auf '{sr}' in D_ItemsStatic — "
                      f"die Zeile gibt es nicht. Unfertiger Spielinhalt; im Scanner "
                      f"bleibt das Feld leer")
        return name, fehler
    ir = (stat[sr].get("Itemable") or {}).get("RowName")
    if not ir or ir not in item or not item[ir].get("DisplayName"):
        fehler.append(f"{name}: D_ItemsStatic.{sr} hat keinen anzeigbaren Namen "
                      f"(Itemable '{ir}')")
    return name, fehler


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

    # Namenskette je freigeschaltetem Vorkommen.
    print()
    for tabelle, zeilen in unser.items():
        if tabelle.startswith("_"):
            continue
        for zeile in zeilen:
            name, kaputt = namenskette(ref, zeile)
            if kaputt:
                for k in kaputt:
                    print(f"FEHLER: {k}")
                fehler += len(kaputt)
            else:
                print(f"ok    {name}: Namenskette vollstaendig "
                      f"(Hervorhebung + Gegenstand haben einen Namen)")

    print(f"\n{fehler} Fehler, {warnungen} Warnungen")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
