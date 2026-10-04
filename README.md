# Ore Scanner Unlock — an Icarus mod

Makes **ruby** and **lithium** deposits show up on the ore scanner you already
craft.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/kroste)

No new items, no scripts, no UE4SS. One field in one game row.

## How it works

Ruby and lithium are already complete deep mining ore deposits in Icarus.
`D_OreDeposit` has a row for each, with its own node materials, its own mining
time and its own highlight — the game even ships the labels **"Deep Mining Ore
Deposit: Ruby"** and **"… Lithium"**. The only thing hiding them from the
scanner is one field in those rows:

```json
"ScannerBlacklist": true
```

Eight of the 26 deposits carry that flag: `Random`, `Exotic`,
`Exotic_Red_Raw`, `Exotic_Raw_Uranium`, `Lithium`, `Ruby`, `Cobalt` and one
mission deposit. All eighteen ordinary ores — iron, gold, copper, silicon,
coal, sulfur, aluminium, titanium, platinum, clay, scoria, obsidian, oxite,
salt, stone, limestone, frozen wood, supercooled ice — do not, and the scanner
shows every one of them.

This mod sets that one field to `false` for both. Nothing else changes: each
row is read out of the game's own table field by field, so node materials,
mining time and highlight stay exactly as the game has them.

### Why only two of the eight

A deposit needs a name at both ends: the `HighlightableRow` names the node, and
the `ResourceType` names what comes out of it. If either is missing the scanner
shows a **blank entry**. Measured against the game's tables, six of the eight
blacklisted deposits fail that:

| Deposit | Why it is left out |
|---|---|
| `Exotic_Red_Raw`, `Exotic_Raw_Uranium` | no `HighlightableRow` at all |
| `Exotic` | no highlight, and marked `bIsDeprecated` |
| `Random` | no highlight, no resource type — a template, not a deposit |
| `Mission_STYX_D_Research2` | mission deposit with its own purpose-built device |
| `Cobalt` | **unfinished game content** — see below |

Uranium already has a dedicated tool in the game, the **Uranium Locator**.

### Cobalt is unfinished, and it shows

Cobalt *looks* ready: `D_OreDeposit` has a `Cobalt` row, `D_Highlightable` has
"Deep Mining Ore Deposit: Cobalt", and `D_Itemable` even has `Item_Cobalt_Ore`
named "Cobalt Ore". But the chain breaks in the middle:
`D_ItemTemplate.Cobalt_Ore` points at a row `Cobalt_Ore` in `D_ItemsStatic`
**that does not exist**. No static row, no item, no name — the scanner lists an
empty entry. No recipe anywhere in the game uses cobalt either, and it occurs
in no region as a vein.

v0.2.0 of this mod shipped cobalt and produced exactly that blank line.
`tools/pruefe-zeilen.py` now walks the whole naming chain and fails on it, so
the next unlock candidate gets caught here rather than in-game.

## What it does not do

- **It finds deposit nodes, not veins.** The scanner shows deep mining ore
  deposits — the things you place a Deep Mining Drill on. Ruby also occurs as
  voxel veins you break with a tier 2 pickaxe (`Ruby_Ore_Normal`,
  `Ruby_Ore_Dense`); the ore scanner never showed those and still doesn't.
- **It does not create deposits.** Nothing here adds ore to a map; it only
  stops the scanner from hiding what is there. See *Where to look* below — on
  Olympus, for instance, neither resource exists at all.
- **It is not a separate ruby-only locator.** The Uranium Locator's behaviour
  lives in a Blueprint class (`BP_ActionableBehaviour_RadiationTracker_C`) that
  is wired to uranium; a data mod cannot retarget it. A dedicated ruby locator
  would need a UE4SS script.

## Where to look

Counted out of `D_VoxelDistributionRegion` — this is the **vein** distribution,
which is the best available hint at where the map puts these resources:

| | Richest spots |
|---|---|
| **Ruby** | Elysium arctic ridges 7.1 %, Elysium and Arkadia arctic caves 3.4 % (dense), arctic surface 1.5 % |
| **Lithium** | Elysium geothermal pools 22.2 % (dense), desert and geothermal caves 7.0 % (dense), desert/geothermal surface 2.2–5.3 % |

Of the four open worlds — Olympus, Styx, Prometheus, Elysium — only **Elysium**
has either resource. Olympus runs on the game's six unprefixed regions, and all
six carry nothing but oxite, silica, sulfur, salt, coal above ground and iron,
copper, coal, platinum, titanium, gold, bauxite below. Prometheus has arctic
terrain but no ruby in any of its six arctic regions. The Arkadia regions exist
in the data but there is no Arkadia prospect to play.

So on an Olympus save this mod changes nothing visible — there is nothing to
show.

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
game has went missing, if a referenced row no longer resolves, or if the
deposit has no displayable name (which is what produced the blank cobalt entry
in v0.2.0). Run both
after an Icarus update rather than editing `src/data/rows.json` by hand.

## Good to know

- Ruby and lithium nodes both reuse the **salt** node materials in the world
  (`M_DeepMiningOreDeposit_Salt_*`), so they look like salt deposits until the
  scanner labels them. That is the game's own asset choice, not something
  this mod changes — and it is a good reason to use the scanner rather than
  trust your eyes.
- This mod **overwrites** a game row rather than adding one. It therefore
  conflicts with any other mod that touches `World/D_OreDeposit` — with merged
  paks, the one that merges last wins.
- The game's ruby deposit has no `MiningTimeSeconds`, so it falls back to the
  table default of 60 seconds; lithium takes 40. Left as is on purpose — this
  mod changes visibility, not balance.

## Credits

Built by **Kroste**. Everything here is read out of Icarus' own data tables;
the mod contains no game assets.

## License

[MIT](LICENSE)
