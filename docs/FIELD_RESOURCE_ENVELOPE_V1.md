# Tampa field resource envelope v1

## Purpose

Translate the frozen prospective designs into **minimum simultaneous field/laboratory resources** before any biological outcome is collected.

This is a logistics document, not an ecological result.

Canonical machine-readable summary:

- `results/field_resource_scenario_requirements_v1.json`

## Protected primary

The authoritative four-bay TNC-v2 programme remains first priority.

At the full 41-node planning frame:

- 3 baseline cores/node;
- **123 outcome-bearing cores** if event and optical are both disabled.

At the exact 36-node confirmatory floor:

- **108 cores**.

Actual preservation/HPLC capacity must be checked against the final node registry, not against the floor if more nodes are collected.

## If a forcing module is confirmatory

Any node in confirmatory event-stress or optical receives the shared pre/post TNC trajectory:

- 3 pre cores;
- 3 post cores;
- post TNC becomes the authoritative TNC-v2 baseline at core-three nodes;
- no third TNC round.

With the full 41-node TNC frame:

- 30 pre/post nodes -> **213 cores** before replacements;
- 33 pre/post nodes -> **222 cores** before replacements.

If event and optical use the same nodes, they share these cores. Do not double-count two separate six-core programmes.

## Event-stress hardware gate

Confirmatory:

- >=30 complete simultaneous temperature+salinity node systems;
- >=8 nodes in each of Old, Middle and Lower Tampa Bay;
- same July 24-September 3 weather window;
- no sequential sensor rotation across different weather windows.

Full planning frame: 33 systems.

If this cannot be met, event-stress is disabled before biological pre-coring.

## Optical-primary hardware gate

Confirmatory:

- >=30 simultaneous within-canopy PAR node systems;
- >=8 nodes in each core bay;
- frozen vertical-profile pilot / geometry / calibration passed;
- same common late-summer window.

Full planning frame: 33 within-canopy systems.

If this cannot be met, the optical biological primary is disabled before biological pre-coring.

## Optical-attribution hardware gate

This is secondary and must not endanger the optical primary.

Confirmatory paired above-canopy attribution requires:

- >=12 simultaneous above-canopy reference systems;
- >=3 per core bay;
- all reference nodes are a subset of optical-primary nodes.

Target: 18 references.

If the reference subset cannot meet 12/3, disable attribution while retaining optical primary if its own gate passes.

Thus the **minimum simultaneous PAR sampling volumes** for optical primary + confirmatory attribution are 30 within-canopy + 12 above-canopy = **42**, unless validated multi-channel hardware supplies more than one synchronized sampling volume per physical unit.

## Resource decision order

1. Pass TNC method/field pilot.
2. Freeze contemporaneous four-bay TNC node registry.
3. Confirm preservation and HPLC capacity for the exact planned core count.
4. Inventory event and PAR systems.
5. Set optional module intent **before biological sampling**:
   - confirmatory only if every frozen simultaneous-capacity/pilot/calendar gate can be met;
   - otherwise disabled.
6. Freeze exact route and sample calendars.
7. Re-run fail-closed readiness validator.

No optional module is allowed to reduce four-bay TNC coverage, widen its seasonal window, weaken HPLC QC, or add an avoidable destructive core round.

## Current implication

The current 16-field STOP state is appropriate because equipment inventory, method-pilot outputs, contemporaneous node eligibility and real laboratory capacity have not been supplied in the repository.

The design is no longer blocked by statistical ambiguity. It is blocked by **physical execution information**.
