# Console and Language Checks — 1.2.4

These scenarios are prepared from the scripts. They have not been run in a Victoria 3 process.

## Preparation

Enable `-debug_mode` in the game's launch options, set the game language to **English**, and fully restart. Begin a non-Ironman Carthaginian game and keep a clean test save.

Use the console for `text` blocks, one command at a time. Use the country inspector's **Script Runner → Effect** for `pdx` blocks.

```text
tag TUN
money 10000000
```

The country should appear as **Punic State**, with Carthage as its capital, Punic culture, the Cult of Tanit, and Dual Suffetes. Check Interventionism, Migration Controls, three frigates, and one naval base level.

## Territorial Government

From a peaceful starting save:

```text
own STATE_CONSTANTINE TUN
```

Allow the relevant checks to run. **Carthage's Territories** should offer **Organize Numidia**. Choose a trading post, a province, or continued direct rule. Only eligible land actually owned by Carthage is transferred.

Each row below is a separate test. Load a clean save to compare mutually exclusive forms.

| Region | Console command |
| --- | --- |
| Tripoli | `own STATE_TRIPOLI TUN` |
| Numidia | `own STATE_CONSTANTINE TUN` |
| Iberia | `own STATE_MURCIA TUN` |
| Gaul | `own STATE_PROVENCE TUN` |
| The Alps | `own STATE_PIEDMONT TUN` |
| Southern Italy | `own STATE_APULIA TUN` |
| Mauretania | `own STATE_FEZ TUN` |
| Egypt | `own STATE_MIDDLE_EGYPT TUN` |
| Phoenicia | `own STATE_LEBANON TUN` |
| Syria | `own STATE_ALEPPO TUN` |
| Mesopotamia | `own STATE_BAGHDAD TUN` |
| Arabia | `own STATE_YEMEN TUN` |

Foundations share a three-month handover. Canceling a foundation should leave other buttons usable. After a successful foundation, their buttons remain visible but unavailable until the handover ends.

To speed up later tests, open the country inspector with `inspect_country TUN` and run:

```pdx
c:TUN = { remove_modifier = crb_territory_disposition_cooldown }
```

This shortcut does not verify natural expiry.

After establishing the Numidian Trading Post, check **Provincialize Numidia**. It should require peace and an expired handover, add 15 Infamy, switch payments from 30% to 50%, remove commercial privileges, and retain the existing country's assets and current Liberty Desire.

The conversion button should disappear, replaced by **Expand the Numidian Province**. Acquiring Oran with `own STATE_ORAN TUN` should let that expansion button transfer only the relevant land.

For the Roman case, establish the Ionian Trading Post and use **Provincialize Rome**. The same country should become the Roman Province (RPR). A separately existing RPR must block conversion without being overwritten or charging Infamy.

## English Text and Icons

- Check the country panel, subject list, relationship tooltip, and concept tooltip. The names must read **Trading Post** and **Province**, with their English descriptions.
- The country relationship retains its graphical icon. Names and territorial buttons must not insert a second text icon.
- Check Governor, Governorship, company names, Prestige Goods, modifiers, and event options.
- No `crb_…`, `je_crb_…`, or `concept_crb_…` keys should appear as labels.
- Check that dynamic names and values render correctly rather than appearing as raw `$…$` or `[…]` expressions.
- Check restored map names and Hanno's matching target names: Mauretania, Cerne, Chretes, and Chariot of the Gods.
- Check that Punic War titles use English ordinals such as **Fourth Punic War**.
- Inspect long event bodies and territorial buttons for clipping.
- Foundation tooltips should highlight the future country and overlord, link the Trading Post or Province concept, and emphasize 30% or 50% payments and the three-month handover. Check both the original regions and the six hidden regions.

Restart in Simplified Chinese and check the same screens, then repeat with an existing save. Both languages should show the same mechanics and numbers, while names and prose follow the selected language.

## Events and Routes

Large event text and quotations should tell the story. Check the Hannibal introduction and the four revenge-route events: their bodies must not state Infamy costs, while the relevant option effects retain the original 10/10/15/20/25 Infamy and claims. Historical dates and elapsed time within the story are legitimate narrative details.

The Cothon planning event should describe the engineers' plans; the construction unlock is explained by the confirmation option's tooltip. Territorial event bodies should retain their local setting, with non-capital-state restrictions shown in the foundation tooltips instead.

To inspect the opening event's English:

```text
event crb_carthage.1 TUN
```

The first conquest should also open the factional struggle. Complete the Barcid route and check that **Hannibal Returns** opens immediately; later adoption of a colonial law should not repeat its introduction.

To arrange the initial French border:

```text
own STATE_ALGIERS FRA
own STATE_CONSTANTINE TUN
```

Allow the border or monthly check to run. **Gauls?** should offer the payments and truce, confrontation, and non-intervention options. All three have five-year policy terms; payments enter both budgets weekly, while relations change once when chosen. A European border alone must not start the event.

For text inspection only:

```text
event crb_flavor.17 TUN
```

Manual event calls do not validate the normal scheduling or border trigger. Hover over all three choices: the agreement shows only its actual weekly payment for five years, +20 relations and a five-year truce; confrontation shows only -50 relations and +10% Kill Rate for five years; non-intervention shows reconsideration in five years. Use the vanilla automatic effect list, country and value formatting, modifier breakdowns, and hover details. No hand-written paragraph should replace those effects; no other policy removals or GDP formulas should appear. The payer and France must have opposite budget entries of exactly the same whole-unit weekly amount for 60 months, without an immediate Treasury transfer. The rate is 0.12% of the payer's GDP, rounded when chosen: 800–900K GDP gives 960–1,080 per week, fixed for the term. France leaving North Africa must clear both payment modifiers on the monthly check while preserving the existing truce. Old saves with the former one-time agreement start payments only on their next choice. Event monetary previews retain vanilla K/M abbreviations; check the small and large values and confirm income/expense colors and durations.

The Cothon's completion event must wait until at least one building level is complete. A level-zero construction site is insufficient.

## Companies and Music

```text
research corporate_charters
```

Meet the company's incorporated-state and building requirements, then establish it through the normal company interface. Check the custom emblem, vanilla industry background, and English names and descriptions.

For a quick company preview in Script Runner:

```pdx
c:TUN = { add_company = company_type:company_crb_carthaginian_trade_house }
```

For music, enable **Carthage**, select **Weighted** mode, and run:

```text
Music.ListTracks
```

Find `crb_carthage_theme`. Its Carthaginian weight is 100000 in January 1836 and 500 afterward; an ordinary other country has weight 1. Startup music requests require a new game and remain subject to the music player's normal restrictions.

## Automated Checks

```sh
python -m unittest discover -s tests -v
```

The bilingual checks require matching keys and language files, valid UTF-8 BOM encoding, complete UI references, intact substitutions and formatting, equal visible numbers, and English values without untranslated Chinese.

## Interest Group Names

Check Interest Group panels, event bodies, journal entries, and effect tooltips. Landholders, Shipowners, Votaries, and Scribes should show their current name without a generic type in parentheses. The same shared format applies to variants in other countries and in Chinese.

## Lebanon's Dedicated Dye Capacity

- In a new campaign, Lebanon should have **15 levels** of Lebanese Dye Plantation potential, with no free constructed levels. Its original **30 arable land** and coal, logging, and fishing potentials remain unchanged.
- Use `own STATE_LEBANON TUN` to test construction. With spare arable land, check vanilla dye production methods, construction costs, workers, and output. Queuing or expanding beyond the regional 15-level resource cap must be blocked by the game's construction rules.
- These plantations still use existing arable land; the regional resource cap and spare-land constraint both apply. Other crops gain no land. The specialized plantation must be unavailable in Syria, Aleppo, and other regions, while vanilla dye-growing regions retain their normal buildings and caps.
- In a pre-update save, allow Lebanon's current owner's monthly check to run, or execute `crb_initialize_lebanon_dye_capacity_effect = yes` in the Effect Script Runner. Repeated calls, save reloads, split ownership, and ownership transfers must retain a total regional potential of 15.
- Three levels of the new plantation should qualify for the Tyrian Purple Company without requiring three textile-mill levels, provided its other conditions are met. Check company prosperity, the Tyrian Purple event's throughput bonus, and Prestige Good output.

Automated checks cover authored initialization, migration, localization, and company integration; the game's combined resource/arable-land construction limits still require in-game testing.
