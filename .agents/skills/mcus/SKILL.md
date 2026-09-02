---
name: mcus
description: "MCUS catalog: look up a microcontroller, select by constraints, compare up to four devices, or report vendor coverage. Use when the Owner wants to pick, look up, or compare MCU parts or 选型. Constraint matching against the MCUS table. Not a Brain Drill and not vector search."
---

# MCUS catalog

Affiliated Skill. Agents query the [MCUS](https://github.com/new-bmp/MCUS) device table. They do not put MCU rows in the Brain, and they do not embed the catalog.

MCUS is one snapshot of product line / device variant / orderable part. Empty fields stay empty.

## When

Owner asks to pick, look up, or compare chips. Coverage questions ("does this snapshot include NXP?").

Brain Drills, Points, and Plans stay on `brain-commands`.

## Catalog

Need `mcu-l-catalog/data/combined/` from a MCUS checkout.

1. `MCUS_CATALOG` if set.
2. Else `--catalog` passed to the script.
3. Else clone once: `git clone --depth 1 https://github.com/new-bmp/MCUS.git /tmp/MCUS` and use `/tmp/MCUS/mcu-l-catalog/data/combined`.

Done when `device-capabilities.csv` and `device-variants.csv` exist in that directory.

## Commands

Run from this skill folder. Print JSON. Do not summarize from memory of the table.

```bash
python3 scripts/query.py --catalog "$CATALOG" lookup STM32F103C8
python3 scripts/query.py --catalog "$CATALOG" select --core Cortex-M4 --min-clock-mhz 120 --min-uart 2 --can --limit 8
python3 scripts/query.py --catalog "$CATALOG" compare allwinner::xr808ct0 st::stm32f103c8
python3 scripts/query.py --catalog "$CATALOG" coverage
```

- **lookup**: one variant or one official part number. Include orderable parts and `missing_key_fields`.
- **select**: hard constraints. A blank numeric field fails a minimum. `--core` is a substring of the core field. `--no-wifi` / `--no-bluetooth` drop rows whose inventory lists those types. Default `--limit 8`.
- **compare**: at most four `device_id`s. Leading numeric cells marked.
- **coverage**: manufacturer row counts from the snapshot. `orderable_part_count=0` means parts were not imported, not that the silicon has none.

## Report

Name the snapshot directory. For each device: manufacturer, variant, core, clock, flash, RAM, FPU, the constraints that matched, and which requested fields were blank. Recommend only rows that passed every stated minimum. Selection index is a sort key, not a benchmark.
