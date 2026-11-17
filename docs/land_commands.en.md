# Land Acquisition and Quick Annexation — 1.3.2

Enter ordinary commands one at a time in the debug console. Paste `pdx` blocks into `inspect_country TUN` → Script Runner → Effect, without an `effect` prefix.

## Annex a Whole Country

```text
tag TUN
annex FRA
```

This annexes France into the country you control. Supply only the target tag after `annex`. Use `annex SPA`, `annex POR`, or `annex TUR` for Spain, Portugal, or the Ottomans. The target must exist in the save.

Paste this entire block into Script Runner to annex several existing countries:

```pdx
c:TUN = {
    if = { limit = { exists = c:FRA } annex = c:FRA }
    if = { limit = { exists = c:SPA } annex = c:SPA }
    if = { limit = { exists = c:POR } annex = c:POR }
    if = { limit = { exists = c:TUR } annex = c:TUR }
    if = { limit = { exists = c:EGY } annex = c:EGY }
    if = { limit = { exists = c:MOR } annex = c:MOR }
    if = { limit = { exists = c:ALD } annex = c:ALD }
    if = { limit = { exists = c:TRI } annex = c:TRI }
    if = { limit = { exists = c:SIC } annex = c:SIC }
    if = { limit = { exists = c:SAR } annex = c:SAR }
    if = { limit = { exists = c:PAP } annex = c:PAP }
    if = { limit = { exists = c:AUS } annex = c:AUS }
    if = { limit = { exists = c:PRU } annex = c:PRU }
    if = { limit = { exists = c:BEL } annex = c:BEL }
    if = { limit = { exists = c:NET } annex = c:NET }
    if = { limit = { exists = c:SWI } annex = c:SWI }
}
```

Use `c:TUN = { annex_with_incorporation = c:FRA }` to inherit the target states’ incorporation. Annexation does not complete journal stages, build ports, or bypass peace and cooldown checks. Use `own` to arrange a smaller test.

## Complete Land Catalog

All 25 territorial jurisdictions are listed below. Including quest-only objectives, the catalog contains 152 distinct state regions.

[Plain console commands](testing/own_all_mod_lands.txt): execute one line at a time.

[Acquire all lands in one execution](testing/own_all_mod_lands.pdx): paste the entire file into the Effect Script Runner. Both transfer whole state regions, including split-state parts, to TUN. Use a pre-foundation test save to avoid reclaiming existing subjects’ holdings.

## Tripolitania — TRP

```text
own STATE_TRIPOLI TUN
own STATE_LIBYA TUN
own STATE_LIBYAN_DESERT TUN
```

## Numidia — NUM

```text
own STATE_ALGIERS TUN
own STATE_CONSTANTINE TUN
own STATE_ORAN TUN
```

## Iberia — IBT

```text
own STATE_MURCIA TUN
own STATE_VALENCIA TUN
own STATE_CATALONIA TUN
own STATE_ARAGON TUN
own STATE_LOWER_ANDALUSIA TUN
own STATE_UPPER_ANDALUSIA TUN
own STATE_NEW_CASTILE TUN
own STATE_OLD_CASTILE TUN
own STATE_LEON TUN
own STATE_EXTREMADURA TUN
own STATE_GALICIA TUN
own STATE_ASTURIAS TUN
own STATE_BASQUE_COUNTRY TUN
```

## Narbonese Gaul — GLT

```text
own STATE_PROVENCE TUN
own STATE_LANGUEDOC TUN
own STATE_RHONE TUN
own STATE_POITOU TUN
own STATE_GUYENNE TUN
own STATE_AUVERGNE_LIMOUSIN TUN
own STATE_BURGUNDY TUN
own STATE_AQUITAINE TUN
```

## Alps / Snow Mountain — SNT

```text
own STATE_WEST_SWITZERLAND TUN
own STATE_EAST_SWITZERLAND TUN
own STATE_SAVOY TUN
own STATE_PIEDMONT TUN
own STATE_LOMBARDY TUN
own STATE_VENETIA TUN
```

## Italy / Rome — IOP, RPR

```text
own STATE_LAZIO TUN
own STATE_ABRUZZO TUN
own STATE_CAMPANIA TUN
own STATE_APULIA TUN
own STATE_CALABRIA TUN
```

## Mauretania — CPM

```text
own STATE_FEZ TUN
own STATE_MARRAKECH TUN
own STATE_AL_RIF TUN
own STATE_INNER_MOROCCO TUN
```

## Egypt — CPE

```text
own STATE_UPPER_EGYPT TUN
own STATE_MIDDLE_EGYPT TUN
own STATE_EGYPTIAN_DESERT TUN
own STATE_MATRUH TUN
own STATE_SINAI TUN
```

## Phoenicia — CPF

```text
own STATE_LEBANON TUN
```

## Syria — CPS

```text
own STATE_SYRIA TUN
own STATE_ALEPPO TUN
own STATE_DEIR_EZ_ZOR TUN
own STATE_PALESTINE TUN
own STATE_TRANSJORDAN TUN
```

## Mesopotamia — CPB

```text
own STATE_MOSUL TUN
own STATE_BAGHDAD TUN
own STATE_BASRA TUN
```

## Arabia — CPA

```text
own STATE_HAIL TUN
own STATE_HEDJAZ TUN
own STATE_YEMEN TUN
own STATE_OMAN TUN
own STATE_ABU_DHABI TUN
```

## Lusitania — XLU

```text
own STATE_ENTRE_DOURO_E_MINHO TUN
own STATE_BEIRA TUN
own STATE_ESTREMADURA TUN
own STATE_ALENTEJO TUN
```

## Etruria — XET

```text
own STATE_TUSCANY TUN
own STATE_UMBRIA TUN
own STATE_EMILIA TUN
own STATE_ROMAGNA TUN
```

## Illyria — XIL

```text
own STATE_ISTRIA TUN
own STATE_DALMATIA TUN
own STATE_CROATIA TUN
own STATE_SLAVONIA TUN
own STATE_SLOVENIA TUN
own STATE_BOSNIA TUN
own STATE_MONTENEGRO TUN
own STATE_ALBANIA TUN
```

## Achaea — XAC

```text
own STATE_ATTICA TUN
own STATE_PELOPONNESE TUN
own STATE_THESSALIA TUN
```

## Macedonia — XMA

```text
own STATE_MACEDONIA TUN
own STATE_SKOPIA TUN
own STATE_KOSOVO TUN
```

## Thrace — XTH

```text
own STATE_EASTERN_THRACE TUN
own STATE_WESTERN_THRACE TUN
```

## Moesia — XMO

```text
own STATE_WESTERN_SERBIA TUN
own STATE_EASTERN_SERBIA TUN
own STATE_BULGARIA TUN
own STATE_NORTHERN_THRACE TUN
own STATE_DOBRUDJA TUN
```

## Dacia — XDA

```text
own STATE_WALLACHIA TUN
own STATE_MOLDAVIA TUN
own STATE_NORTHERN_TRANSYLVANIA TUN
own STATE_SOUTHERN_TRANSYLVANIA TUN
own STATE_BUKOVINA TUN
```

## Pannonia — XPA

```text
own STATE_CENTRAL_HUNGARY TUN
own STATE_BEKES TUN
own STATE_TRANSDANUBIA TUN
own STATE_DELVIDEK TUN
own STATE_BANAT TUN
own STATE_SLOVAKIA TUN
own STATE_RUTHENIA TUN
```

## Noricum — XNO

```text
own STATE_AUSTRIA TUN
own STATE_STYRIA TUN
own STATE_TYROL TUN
own STATE_SOUTH_TYROL TUN
```

## Belgica — XBE

```text
own STATE_FLANDERS TUN
own STATE_WALLONIA TUN
own STATE_HOLLAND TUN
own STATE_FRIESLAND TUN
own STATE_GELRE TUN
```

## Germania — XGE

```text
own STATE_POMERANIA TUN
own STATE_ELBE TUN
own STATE_WESTPHALIA TUN
own STATE_ANHALT TUN
own STATE_RHINELAND TUN
own STATE_NORTH_RHINE TUN
own STATE_BRANDENBURG TUN
own STATE_SCHLESWIG_HOLSTEIN TUN
own STATE_WURTTEMBERG TUN
own STATE_BADEN TUN
own STATE_HANNOVER TUN
own STATE_BRUNSWICK TUN
own STATE_BAVARIA TUN
own STATE_FRANCONIA TUN
own STATE_SAXONY TUN
own STATE_HESSE TUN
own STATE_MECKLENBURG TUN
own STATE_RUHR TUN
own STATE_LOWER_SILESIA TUN
own STATE_UPPER_SILESIA TUN
own STATE_WEST_PRUSSIA TUN
own STATE_EAST_PRUSSIA TUN
```

## Lugdunensian Gaul — XLG

```text
own STATE_ILE_DE_FRANCE TUN
own STATE_NORMANDY TUN
own STATE_PICARDY TUN
own STATE_ALSACE_LORRAINE TUN
own STATE_BRITTANY TUN
own STATE_CHAMPAGNE TUN
own STATE_FRANCHE_COMTE TUN
own STATE_LORRAINE TUN
own STATE_ORLEANS TUN
own STATE_MAINE_ANJOU TUN
own STATE_FRENCH_LOW_COUNTRIES TUN
```

## Quest Objectives

Hannibal and revenge objectives accept actual marked subjects’ holdings. Hanno requires direct Carthaginian ownership, and Western Sahara also needs a completed port. Advance revenge stages in order; the Roman conclusion requires peace. The three New Carthage states are an example of meeting its three-state threshold.

### hannibal / Tripolitania

```text
own STATE_TRIPOLI TUN
own STATE_LIBYA TUN
```

### hannibal / Numidia

```text
own STATE_ALGIERS TUN
own STATE_CONSTANTINE TUN
own STATE_ORAN TUN
```

### hannibal / Syracuse

```text
own STATE_SICILY TUN
```

### hannibal / Mediterranean Islands

```text
own STATE_BALEARIC_ISLANDS TUN
own STATE_MALTA TUN
own STATE_CRETE TUN
own STATE_CYPRUS TUN
```

### hannibal / Iberian foothold

```text
own STATE_LOWER_ANDALUSIA TUN
```

### hannibal / New Carthage

```text
own STATE_MURCIA TUN
own STATE_VALENCIA TUN
own STATE_CATALONIA TUN
```

### hannibal / Tyre

```text
own STATE_LEBANON TUN
```

### revenge / After the Pyrenees button

```text
own STATE_CATALONIA TUN
own STATE_VALENCIA TUN
own STATE_MURCIA TUN
own STATE_UPPER_ANDALUSIA TUN
own STATE_LOWER_ANDALUSIA TUN
```

### revenge / After the Gaul button

```text
own STATE_LANGUEDOC TUN
own STATE_PROVENCE TUN
own STATE_RHONE TUN
```

### revenge / After the Alps button

```text
own STATE_WEST_SWITZERLAND TUN
own STATE_EAST_SWITZERLAND TUN
own STATE_SAVOY TUN
own STATE_PIEDMONT TUN
own STATE_LOMBARDY TUN
own STATE_VENETIA TUN
```

### revenge / After the revenge button

```text
own STATE_LAZIO TUN
```

### hanno / Lixus

```text
own STATE_FEZ TUN
```

### hanno / Kerne Trading Post

```text
own STATE_WEST_SAHARA TUN
```

### hanno / River Chretes

```text
own STATE_SENEGAL TUN
```

### hanno / Chariot of the Gods

```text
own STATE_SOUTH_CAMEROON TUN
```

## Reclaim a Custom Subject

First run `tag TUN`, then choose an existing target below.

| Subject | Annex command |
| --- | --- |
| Tripolitania | `annex TRP` |
| Numidia | `annex NUM` |
| Iberia | `annex IBT` |
| Narbonese Gaul | `annex GLT` |
| Alps / Snow Mountain | `annex SNT` |
| Italy / Rome | `annex IOP`, `annex RPR` |
| Mauretania | `annex CPM` |
| Egypt | `annex CPE` |
| Phoenicia | `annex CPF` |
| Syria | `annex CPS` |
| Mesopotamia | `annex CPB` |
| Arabia | `annex CPA` |
| Lusitania | `annex XLU` |
| Etruria | `annex XET` |
| Illyria | `annex XIL` |
| Achaea | `annex XAC` |
| Macedonia | `annex XMA` |
| Thrace | `annex XTH` |
| Moesia | `annex XMO` |
| Dacia | `annex XDA` |
| Pannonia | `annex XPA` |
| Noricum | `annex XNO` |
| Belgica | `annex XBE` |
| Germania | `annex XGE` |
| Lugdunensian Gaul | `annex XLG` |

Common vanilla tags: France FRA, Spain SPA, Portugal POR, Ottomans TUR, Egypt EGY, Morocco MOR, Algiers ALD, Tripolitania TRI, Two Sicilies SIC, Sardinia-Piedmont SAR, Papal States PAP, Austria AUS, Prussia PRU, Belgium BEL, Netherlands NET, Switzerland SWI, Britain GBR, Russia RUS, United States USA. Vanilla TRI and the mod’s TRP are different countries.

## References

[1.15 effects](https://github.com/Victoria-3-Modding-Co-op/Modding-Digests/blob/b4e1e105a8003e4b9c11488b938931d6e89d4985/1.15.0/docs/effects.log) · [Console syntax](https://vic3.paradoxwikis.com/Console_commands)
