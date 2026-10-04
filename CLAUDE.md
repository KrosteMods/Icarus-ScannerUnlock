# CLAUDE.md

Hinweise für Claude Code (claude.ai/code) bei Arbeit an diesem Repo.

## Grundlagen

- **Was:** Datentabellen-Mod für Icarus, die Rubin-, Lithium- und
  Cobalt-Vorkommen vom Erz-Scanner anzeigen lässt. Kein neues Item, kein
  Skript, kein UE4SS — ein Feld in drei Spielzeilen.
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

### Warum nur drei der acht gesperrten Zeilen (v0.2.0)

Lars: „die anderen auch". Nachgemessen, bevor gebaut wurde — und die Messung
hat die Hälfte der Liste aussortiert. Der Scanner benennt ein Vorkommen über
`HighlightableRow`. In `D_Highlightable` gibt es **22** Zeilen
`Deep_Mining_Ore_Deposit_*`, darunter Ruby, Lithium und Cobalt. Genau **vier**
der acht gesperrten Vorkommen haben gar keine eigene Hervorhebung: `Random`,
`Exotic`, `Exotic_Red_Raw`, `Exotic_Raw_Uranium`. Ohne Hervorhebung hat der
Scanner nichts zu benennen; die Sperre dort zu lösen ist voraussichtlich
wirkungslos. Dazu:

- `Exotic` trägt `Metadata.bIsDeprecated: true` — eine abgelegte Zeile.
- `Random` ist eine Vorlage, kein echtes Vorkommen.
- `Mission_STYX_D_Research2` hat ein eigenes Gerät im Spiel („Monitoring
  Device").
- Uran hat mit dem Uran-Lokalisator schon ein eigenes Werkzeug.

Geliefert werden deshalb Ruby, Lithium, Cobalt — die drei, die durchgehend
vorbereitet und nur gesperrt sind. **Die Lehre:** „alle vom selben Typ"
freizuschalten klingt wie dieselbe Arbeit, ist aber eine Massenänderung nach
Strukturmerkmal. Erst auflisten, was das Muster trifft, dann auf die weisse
Liste umstellen.

Nebenbei aufgefallen: `Deep_Mining_Ore_Deposit_Lead` und `_Abyssal_Oxite`
existieren als Hervorhebung, ohne dass es ein passendes Vorkommen gibt — Reste,
für diese Mod ohne Bedeutung.

### Die beiden Scanner des Spiels

- **Deep Mining Ore Scanner** (`Scanner_DeepOre`): Rezept `Deep_Ore_Scanner` an
  Fabricator und Manufacturer, 10 Steel_Ingot + 4 Electronics + 16 Steel_Screw
  + 30 Copper_Wire, 10.000 mJ. Zeigt, was in der Nähe liegt.
- **Advanced Deep Mining Ore Scanner** (`Meta_Scanner_DeepOre`): Workshop, 500
  Credits Forschung, 250 Replikation, Verhalten `Scanner_DeepOre_Advanced`. Die
  Beschreibung sagt „can be programmed to locate **specific** deep ore
  deposits" — das ist der, mit dem man gezielt nach Rubin sucht.

Beide hängen am selben `D_OreDeposit` und damit am selben Feld.

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
- **Der Merged-Pak trägt GANZE Tabellen, nicht einzelne Zeilen.** Nachgemessen
  beim Einbau am 04.10.2026: der Pak wuchs beim Hinzufügen dieser Mod um
  **19.354 Byte**, die vollständige 26-zeilige `D_OreDeposit` ist kompakt
  **19.230 Byte** groß — Verhältnis 1,01. Das ist die wichtige Zusicherung:
  hätte lmm nur unsere eine Zeile hineingeschrieben, würde der Pak die Tabelle
  ersetzen und die anderen 25 Vorkommen aus dem Spiel nehmen. Diese Rechnung
  gehört nach jedem Umbau der Merge-Kette wiederholt; ein Blick auf
  `strings | grep -c` genügt **nicht**, der Inhalt liegt komprimiert und zählt
  immer nur einmal.
- Daraus folgt direkt die Regel aus der README: **nach jedem Icarus-Update neu
  bauen** (`lmm verify --game icarus --fix`). Eine alte gemergte Tabelle setzt
  sonst alle 26 Vorkommen auf den Stand des vorigen Patches zurück, nicht nur
  unsere Zeile.

## Grenzen, die in der README stehen und keine Fehler sind

- Der Scanner findet **Tiefbau-Knoten**, nicht die Rubin-Adern im Fels
  (`Ruby_Ore_Normal`/`Ruby_Ore_Dense`, Spitzhacke T2). Das war schon vorher so.
- Rubin liegt nur in arktischen Regionen von Elysium und Arkadia samt Graten
  und Höhlen. Ohne arktisches Gelände gibt es nichts zu finden.
- Die Rubin-Knoten benutzen die **Salz**-Materialien des Spiels, sehen also wie
  Salz aus. Das ist die Asset-Wahl des Spiels, nicht unsere.
