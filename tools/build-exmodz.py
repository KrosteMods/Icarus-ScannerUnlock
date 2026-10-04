#!/usr/bin/env python3
"""Setzt aus src/data/rows.json das .EXMODZ-Buendel zusammen.

Format (am Buendel einer vorhandenen Mod abgelesen, 04.10.2026):

    <name>.EXMODZ                       ein ZIP
      Extracted Mods/<name>.EXMOD       JSON: Kopfdaten + "Rows"

`Rows` ist eine Liste von `{ "CurrentFile": "<Tabelle>.json", "File_Items": [...] }`.
In `CurrentFile` steht der Pfad der Spieltabelle mit `-` statt `/`, also
`World-D_OreDeposit.json` fuer `World/D_OreDeposit.json`.

Aufruf:  python3 tools/build-exmodz.py [ziel-ordner]
"""
import json, pathlib, sys, zipfile

NAME = "ScannerUnlock"
WURZEL = pathlib.Path(__file__).resolve().parent.parent


def main():
    ziel = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else WURZEL / "dist"
    ziel.mkdir(parents=True, exist_ok=True)

    rows = json.loads((WURZEL / "src/data/rows.json").read_text(encoding="utf-8"))
    version = (WURZEL / "VERSION").read_text(encoding="utf-8").strip()
    frei = [z["Name"] for t, zl in rows.items() if not t.startswith("_") for z in zl]

    manifest = {
        "name": "Ore Scanner Unlock",
        "author": "Kroste",
        "version": version,
        "description": ("Takes deposits off the ore scanner's blacklist so the game's own "
                        "scanner shows them. Unlocked: " + ", ".join(frei) + "."),
        "fileName": NAME,
        "readmeURL": "https://github.com/KrosteMods/Icarus-ScannerUnlock",
        "imageURL": "",
        # Level2 heisst in diesem Format: die Zeilen stehen direkt im Manifest,
        # nicht als einzelne Dateien daneben.
        "Level2": "True",
        "Rows": [
            {"CurrentFile": f"{tabelle}.json", "File_Items": zeilen}
            for tabelle, zeilen in rows.items() if not tabelle.startswith("_")
        ],
    }

    aus = ziel / f"{NAME}.EXMODZ"
    with zipfile.ZipFile(aus, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"Extracted Mods/{NAME}.EXMOD",
                   json.dumps(manifest, indent=4, ensure_ascii=False))

    zeilenAnzahl = sum(len(r["File_Items"]) for r in manifest["Rows"])
    print(f"{aus}  ({aus.stat().st_size} Byte, {len(manifest['Rows'])} Tabelle(n), "
          f"{zeilenAnzahl} Zeile(n): {', '.join(frei)})")


if __name__ == "__main__":
    main()
