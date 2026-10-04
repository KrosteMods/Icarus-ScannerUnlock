# CLAUDE.md

Hinweise für Claude Code (claude.ai/code) bei Arbeit an diesem Repo.

## Grundlagen

- **Was:** Datentabellen-Mod für Icarus, die Rubin-Vorkommen vom Erz-Scanner
  anzeigen lässt. Kein neues Item, kein Skript, kein UE4SS — ein Feld in einer
  Spielzeile.
- **Repo:** `github.com/KrosteMods/Icarus-ScannerUnlock`. Mods gehören in die
  KrosteMods-Org, nicht nach KroModIx.
- **Auslieferung:** `.EXMODZ` als Release-Datei. Das ist ein ZIP mit
  `Extracted Mods/ScannerUnlock.EXMOD` darin, einem JSON-Manifest mit
  `Level2: "True"` und einer `Rows`-Liste.
- **Kommunikation:** Deutsch, „du". Lars entwirft, Claude implementiert.
  README und Release-Texte auf Englisch, Code-Kommentare und diese Datei auf
  Deutsch.

## Befehle

```bash
python3 tools/erzeuge-zeilen.py <referenz> [Ruby,Lithium,...]  # Zeilen erzeugen
python3 tools/pruefe-zeilen.py <referenz>                      # gegen Spieldaten prüfen
python3 tools/build-exmodz.py                                  # Bündel bauen
```

`<referenz>` ist ein Ordner mit den entpackten Spieltabellen als JSON
(`World-D_OreDeposit.json` usw.). Liegt bei mir unter
`../Icarus-OreRouter/reference` und ist bewusst nicht im Repo: er ist aus einem
kommerziellen Spiel erzeugt.

## Der Befund, auf dem die Mod steht (04.10.2026)

Lars fragte, ob man zum Uran-Lokalisator auch einen für Rubine machen kann.
Gemessen an den Spieldaten, nicht geraten:

- `D_OreDeposit` hat **26** Vorkommen, darunter eine vollständige Zeile `Ruby`
  mit `ResourceType: Ruby_Ore`, Knotenmaterialien und
  `HighlightableRow: Deep_Mining_Ore_Deposit_Ruby`. In `D_Highlightable` steht
  dazu der Anzeigename **„Deep Mining Ore Deposit: Ruby"**. Das Spiel ist also
  komplett vorbereitet.
- Genau **acht** Zeilen tragen `ScannerBlacklist: true` — `Random`, `Exotic`,
  `Exotic_Red_Raw`, `Exotic_Raw_Uranium`, `Lithium`, `Ruby`, `Cobalt` und ein
  Missions-Vorkommen. Die **achtzehn** gewöhnlichen Erze tragen es nicht.
- Der Uran-Lokalisator ist ein eigener Weg und für Daten nicht zu haben:
  `Radiation_Tracker` → `Actionable: Radiation_Tracker` → `D_Actions` →
  `BP_ActionableBehaviour_RadiationTracker_C`. Das Verhalten steckt in einer
  Blueprint-Klasse, fest auf Uran. Ein neues Item könnte nur auf
  `Scanner_DeepOre` zeigen und wäre damit ein zweiter Erz-Scanner.

**Was davon Hypothese ist:** dass der Scanner das Feld tatsächlich ausliest.
Das Verhalten liegt in `BP_ActionableBehaviour_Scanner_DeepOre_C` und ist von
außen nicht lesbar. Belegt sind das Feld, seine Verteilung über die 26 Zeilen
und die fertige Hervorhebung — das ist starke Indizienlage, kein Beweis. Steht
der Befund im Spiel, gehört dieser Absatz umgeschrieben.

## Invarianten

- **Die Zeile wird erzeugt, nicht getippt.** Diese Mod *überschreibt* eine
  Spielzeile. Ein von Hand abgeschriebenes Feld würde beim nächsten Patch
  veralten, und ein **vergessenes** Feld setzt das Spiel still auf den
  Tabellen-Default zurück — dann fehlt im Spiel ein Knotenmaterial, ohne
  Fehlermeldung. `tools/erzeuge-zeilen.py` liest die echte Zeile und ändert
  genau ein Feld.
- **`pruefe-zeilen.py` prüft vier Dinge**, und jedes davon ist ein real
  möglicher Fehler: erfundene Feldnamen, fehlende Felder aus der Spielzeile,
  mehr als die eine gewollte Abweichung, und unauflösbare Verweise.
  **Zwei Löcher hatte der erste Entwurf**, beide durch Gegenprobe gefunden:
  (1) Verweise wurden übersprungen, weil in den Spielzeilen nur `RowName`
  steht und der Tabellenname aus `Defaults` kommt — die Schleife prüfte nichts
  und meldete „0 Fehler". (2) Ein Feld, das die Spielzeile nicht hat, das es
  aber in `Defaults` gibt, rutschte durch, weil die Namensprüfung
  Default-Felder erlaubt. Nach jeder Änderung am Prüfer wieder gegenprüfen:
  Feld erfinden, Feld löschen, Verweis verbiegen, Default-Feld zusätzlich
  setzen — alle vier müssen rot werden.
- **Nach einem Icarus-Update erst erzeugen, dann prüfen, dann bauen.** Die
  Tabellen ändern sich; eine alte Zeile überschreibt sonst eine neuere.
- **Der Referenzordner kommt nicht ins Repo** (`.gitignore`): er ist aus dem
  Spiel erzeugt.

## Grenzen, die in der README stehen und keine Fehler sind

- Der Scanner findet **Tiefbau-Knoten**, nicht die Rubin-Adern im Fels
  (`Ruby_Ore_Normal`/`Ruby_Ore_Dense`, Spitzhacke T2). Das war schon vorher so.
- Rubin liegt nur in arktischen Regionen von Elysium und Arkadia samt Graten
  und Höhlen. Ohne arktisches Gelände gibt es nichts zu finden.
- Die Rubin-Knoten benutzen die **Salz**-Materialien des Spiels, sehen also wie
  Salz aus. Das ist die Asset-Wahl des Spiels, nicht unsere.
