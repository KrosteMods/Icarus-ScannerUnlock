# Ore Scanner Unlock — an Icarus mod

Makes **ruby**, **lithium** and **cobalt** deposits show up on the ore scanner
you already craft.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kroste)

No new items, no scripts, no UE4SS. One field in one game row.

## How it works

Ruby, lithium and cobalt are already complete deep mining ore deposits in
Icarus. `D_OreDeposit` has a row for each, with its own node materials, its own
mining time and its own highlight — the game even ships the labels **"Deep
Mining Ore Deposit: Ruby"**, **"… Lithium"** and **"… Cobalt"**. The only thing
hiding them from the scanner is one field in those rows:

```json
"ScannerBlacklist": true
```

Eight of the 26 deposits carry that flag: `Random`, `Exotic`,
`Exotic_Red_Raw`, `Exotic_Raw_Uranium`, `Lithium`, `Ruby`, `Cobalt` and one
mission deposit. All eighteen ordinary ores — iron, gold, copper, silicon,
coal, sulfur, aluminium, titanium, platinum, clay, scoria, obsidian, oxite,
salt, stone, limestone, frozen wood, supercooled ice — do not, and the scanner
shows every one of them.

This mod sets that one field to `false` for the three. Nothing else changes:
each row is read out of the game's own table field by field, so node materials,
mining time and highlight stay exactly as the game has them.

### Why only three of the eight

The scanner names a deposit through its `HighlightableRow`. Measured against
`D_Highlightable`: exactly **four** of the eight blacklisted rows have no
highlight of their own — `Random`, `Exotic`, `Exotic_Red_Raw` and
`Exotic_Raw_Uranium`. Without one there is nothing for the scanner to label, so
lifting their flag is not expected to achieve anything. On top of that,
`Exotic` is marked `bIsDeprecated` in the game data, `Random` is a template
rather than a real deposit, and the mission deposit has its own purpose-built
device. Ruby, lithium and cobalt are prepared end to end and only blacklisted —
those are the three worth unlocking.

Uranium already has a dedicated tool in the game, the **Uranium Locator**.

## What it does not do

- **It finds deposit nodes, not veins.** The scanner shows deep mining ore
  deposits — the things you place a Deep Mining Drill on. Ruby also occurs as
  voxel veins you break with a tier 2 pickaxe (`Ruby_Ore_Normal`,
  `Ruby_Ore_Dense`); the ore scanner never showed those and still doesn't.
- **It does not create deposits.** Ruby is placed in **arctic** regions of
  Elysium and Arkadia, including their ridges and caves. On a prospect without
  arctic terrain there is nothing to find, and the same goes for wherever the
  map does or does not place lithium and cobalt.
- **It is not a separate ruby-only locator.** The Uranium Locator's behaviour
  lives in a Blueprint class (`BP_ActionableBehaviour_RadiationTracker_C`) that
  is wired to uranium; a data mod cannot retarget it. A dedicated ruby locator
  would need a UE4SS script.

## Requirements

- **Icarus** with the **Dangerous Horizons** content — all three deposit rows
  are gated behind that feature level. Tested against Icarus 3.0.30.
- An **ore scanner** in hand. Two exist and both read the same deposit list:
  - **Deep Mining Ore Scanner** — crafted at a Fabricator or Manufacturer from
    10 Steel Ingot, 4 Electronics, 16 Steel Screw, 30 Copper Wire. Shows
    whatever deposits are nearby.
  - **Advanced Deep Mining Ore Scanner** — a workshop item (500 credits to
    research, 250 to replicate). The game describes it as programmable for a
    *specific* deposit type, so this is the one to use if you want to hunt ruby
    alone rather than every deposit at once.
- A mod manager that can **apply/deploy** `.EXMODZ` data mods, so a merged pak
  ends up in `Icarus/Content/Paks/mods`. Importing alone is not enough.
  On Linux: [lmm](https://github.com/DonovanMods/linux-mod-manager)
  (`lmm import ScannerUnlock.EXMODZ --game icarus && lmm deploy`), or the
  Icarus plugin for [KroModIx](https://github.com/KroModIx/KroModIx).
  On Windows: the Icarus Mod Manager.

Multiplayer: the scanner reads world data, so **the host** needs the mod.

## Install

1. Download `ScannerUnlock.EXMODZ` from the
   [releases](https://github.com/KrosteMods/Icarus-ScannerUnlock/releases).
2. Import it in your mod manager and **apply/deploy** the profile.
3. Start the game and use an ore scanner.

Rebuild the merged pak after every Icarus update (`lmm verify --game icarus
--fix`), otherwise the mod sits on top of the previous patch's tables.

## Changing the set

The flag is the same for every deposit. Regenerate with the ones you want and
rebuild:

```bash
python3 tools/erzeuge-zeilen.py <folder-with-extracted-game-tables> Ruby,Lithium
python3 tools/pruefe-zeilen.py <folder-with-extracted-game-tables>
python3 tools/build-exmodz.py
```

`erzeuge-zeilen.py` copies the row out of the game's table and changes exactly
one field; `pruefe-zeilen.py` fails if anything else differs, if a field the
game has went missing, or if a referenced row no longer resolves. Run both
after an Icarus update rather than editing `src/data/rows.json` by hand.

## Good to know

- Ruby, lithium and cobalt nodes all reuse the **salt** node materials in the
  world (`M_DeepMiningOreDeposit_Salt_*`), so they look like salt deposits until
  the scanner labels them. That is the game's own asset choice, not something
  this mod changes — and it is a good reason to use the scanner rather than
  trust your eyes.
- This mod **overwrites** a game row rather than adding one. It therefore
  conflicts with any other mod that touches `World/D_OreDeposit` — with merged
  paks, the one that merges last wins.
- The game's ruby deposit has no `MiningTimeSeconds`, so it falls back to the
  table default of 60 seconds; lithium and cobalt take 40. Left as is on
  purpose — this mod changes visibility, not balance.

## Credits

Built by **Kroste**. Everything here is read out of Icarus' own data tables;
the mod contains no game assets.

## License

[MIT](LICENSE)
